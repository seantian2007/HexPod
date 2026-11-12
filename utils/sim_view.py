"""
SIM 可视化工具（teleop 专用）

这个文件里有三样东西：
  1. LiveView     —— teleop 运行时实时画的 pygame 窗口（俯视、世界坐标、镜头跟随机器人）
  2. KeyboardPad  —— 手柄读不到时用键盘代替（接口和 GamePad 一样：read(dt) / quit_pressed()）
  3. replay(path) —— 跑完以后读 teleop_log.npz，用 matplotlib 画总览图 + 3D 回放动画

用法：
  view = LiveView(rate=50)
  每一帧：view.update(feet, walker.was_stance, cmd, thetas, prev)
  退出：  view.closed 为 True（关窗口或按 Esc）

  python3 -m utils.sim_view                  # 回放默认的 teleop_log.npz
  python3 -m utils.sim_view my_log.npz       # 回放指定文件
"""
import sys
import numpy as np

from .body_ik import a as ALPHA, m as MOUNT

LEG_NAMES = ['R1', 'R2', 'R3', 'L1', 'L2', 'L3']
# RGB, 0-255。右腿暖色、左腿冷色，一眼能分左右
LEG_RGB = [(230, 85, 70), (240, 150, 50), (205, 170, 40),
           (60, 130, 220), (60, 175, 170), (130, 100, 210)]
HEX_ORDER = [0, 1, 2, 5, 4, 3]          # 绕机身一圈：R1 R2 R3 L3 L2 L1


# ---------------------------------------------------------------------------
# 共用的小函数（LiveView 和 replay 都用）
# ---------------------------------------------------------------------------
def body_to_world(p_xy, X, Y, psi):
    """机身系 xy → 世界系 xy。p_xy: (..., 2)。psi 是航向角（rad，CCW 为正）。"""
    c, s = np.cos(psi), np.sin(psi)
    R = np.array([[c, -s], [s, c]])
    return p_xy @ R.T + np.array([X, Y])


def integrate_pose(cmd, dt):
    """把每帧的 (vx, vy, w) 积分成机身在世界里的位姿。
    cmd: (N, 3)，vx/vy 是机身系 mm/s，w 是 °/s。返回 (N, 3)：X, Y (mm), psi (rad)。
    这就是阶段 6 Q5 的运动学：v 在机身系，要先转到世界系再积分。"""
    pose = np.zeros((len(cmd), 3))
    X = Y = psi = 0.0
    for k, (vx, vy, w) in enumerate(cmd):
        c, s = np.cos(psi), np.sin(psi)
        X += (c * vx - s * vy) * dt
        Y += (s * vx + c * vy) * dt
        psi += np.radians(w) * dt
        pose[k] = X, Y, psi
    return pose


def support_polygon(pts):
    """着地脚 (n, 2) 按逆时针排好。少于 3 只脚返回 None。"""
    if len(pts) < 3:
        return None
    c = pts.mean(axis=0)
    return pts[np.argsort(np.arctan2(pts[:, 1] - c[1], pts[:, 0] - c[0]))]


def stability_margin(pts):
    """重心投影（机身原点）到支撑多边形最近边的有符号距离，>0 在里面。pts 是机身系。"""
    P = support_polygon(pts)
    if P is None:
        return np.nan
    d = []
    for k in range(len(P)):
        p, q = P[k], P[(k + 1) % len(P)]
        e = q - p
        n_in = np.array([-e[1], e[0]]) / np.linalg.norm(e)
        d.append(np.dot(-p, n_in))
    return min(d)


# ---------------------------------------------------------------------------
# 1. LiveView：运行时的实时俯视图
# ---------------------------------------------------------------------------
class LiveView:
    """pygame 窗口。画面（从下往上一层层画）：
       网格（世界固定，机器人走时网格往后退，就能看出在动）
       → 机身走过的路径 → 历史脚印（越旧越淡）
       → 支撑多边形（绿=稳，红=重心出界）+ 稳定裕度
       → 机身六边形 + 六条腿（实心=着地，空心=摆动，圈越大抬得越高）
       → 速度箭头 + 转向中心 ICR
       → 左上角仪表（命令、关节速度、裕度）+ 底部滚动步态图
    """

    def __init__(self, rate=50, v_max=40, w_max=15, size=(1000, 720),
                 px_per_mm=0.7, draw_every=2, speed_limit=100):
        import pygame
        self.pg = pygame
        pygame.init()
        self.screen = pygame.display.set_mode(size)
        pygame.display.set_caption('HexPod teleop - SIM')
        self.font = pygame.font.SysFont('menlo,consolas,dejavusansmono,monospace', 15)
        self.big = pygame.font.SysFont('menlo,consolas,dejavusansmono,monospace', 18, bold=True)
        self.W, self.H = size
        self.dt = 1 / rate
        self.v_max, self.w_max, self.limit = v_max, w_max, speed_limit
        self.s = px_per_mm
        self.draw_every = draw_every
        self.closed = False

        self.k = 0                                  # 帧号
        self.X = self.Y = self.psi = 0.0            # 机身在世界里的位姿
        self.path = []                              # 机身走过的点
        self.prints = []                            # (x, y, 腿号, 落地帧号)
        self.prev_stance = np.ones(6, dtype=bool)
        self.z0 = None
        self.gait_hist = np.ones((int(4 * rate), 6), dtype=bool)   # 最近 4 秒的着地情况
        self.peak = 0.0                             # 整个过程的最大关节速度

    # 世界坐标 (mm) → 屏幕像素。镜头中心跟着机身，世界 x 朝右、y 朝上
    def _px(self, xy):
        xy = np.atleast_2d(xy)
        sx = self.W / 2 + (xy[:, 0] - self.X) * self.s
        sy = self.H / 2 + 40 - (xy[:, 1] - self.Y) * self.s
        return np.stack([sx, sy], axis=1)

    def update(self, feet, stance, cmd, thetas=None, prev=None):
        """每帧调用一次。feet: (6,3) 机身系；stance: (6,) bool；cmd: (vx, vy, w)；
        thetas/prev: (18,) 本帧和上一帧的角度（只用来显示关节速度，可以不传）。"""
        pg = self.pg
        for e in pg.event.get((pg.QUIT, pg.KEYDOWN)):
            if e.type == pg.QUIT or (e.type == pg.KEYDOWN and e.key == pg.K_ESCAPE):
                self.closed = True

        vx, vy, w = cmd
        stance = np.asarray(stance, dtype=bool)
        if self.z0 is None:
            self.z0 = feet[:, 2].min()

        # --- 状态更新（每帧都做，不管画不画）---
        c, s = np.cos(self.psi), np.sin(self.psi)
        self.X += (c * vx - s * vy) * self.dt
        self.Y += (s * vx + c * vy) * self.dt
        self.psi += np.radians(w) * self.dt
        if self.k % 5 == 0:
            self.path.append((self.X, self.Y))
            self.path = self.path[-600:]

        feet_w = body_to_world(feet[:, :2], self.X, self.Y, self.psi)
        for i in np.where(stance & ~self.prev_stance)[0]:       # 刚落地的脚留一个脚印
            self.prints.append((*feet_w[i], i, self.k))
        self.prints = self.prints[-90:]
        self.prev_stance = stance.copy()
        self.gait_hist = np.roll(self.gait_hist, -1, axis=0)
        self.gait_hist[-1] = stance

        rate_now = 0.0
        if thetas is not None and prev is not None:
            rate_now = np.max(np.abs(np.asarray(thetas) - np.asarray(prev))) / self.dt
            self.peak = max(self.peak, rate_now)
        margin = stability_margin(feet[stance, :2])

        self.k += 1
        if (self.k - 1) % self.draw_every:
            return
        self._draw(feet, feet_w, stance, (vx, vy, w), rate_now, margin)

    # -----------------------------------------------------------------------
    def _draw(self, feet, feet_w, stance, cmd, rate_now, margin):
        pg, scr = self.pg, self.screen
        vx, vy, w = cmd
        scr.fill((246, 247, 249))

        # 网格：每 100 mm 一条细线，每 500 mm 一条粗线
        half_w, half_h = self.W / 2 / self.s, self.H / 2 / self.s
        for g in np.arange(np.floor((self.X - half_w) / 100) * 100, self.X + half_w + 100, 100):
            x = self._px([g, 0])[0, 0]
            pg.draw.line(scr, (214, 218, 224) if g % 500 == 0 else (232, 235, 239), (x, 0), (x, self.H))
        for g in np.arange(np.floor((self.Y - half_h) / 100) * 100, self.Y + half_h + 200, 100):
            y = self._px([0, g])[0, 1]
            pg.draw.line(scr, (214, 218, 224) if g % 500 == 0 else (232, 235, 239), (0, y), (self.W, y))

        # 半透明的东西要先画在带 alpha 的 Surface 上再贴到屏幕。
        # 注意 pygame 在 alpha 层上画图是“覆盖”不是“混合”，所以支撑多边形单独一层先贴，路径和脚印再贴在上面
        layer = pg.Surface((self.W, self.H), pg.SRCALPHA)

        # 支撑多边形
        P = support_polygon(feet_w[stance])
        if P is not None:
            ok = margin > 0
            fill = (70, 180, 110, 60) if ok else (220, 70, 70, 80)
            edge = (50, 150, 90, 220) if ok else (200, 50, 50, 230)
            pts = self._px(P)
            pg.draw.polygon(layer, fill, pts)
            pg.draw.polygon(layer, edge, pts, 2)
        scr.blit(layer, (0, 0))
        layer.fill((0, 0, 0, 0))

        # 机身路径
        if len(self.path) > 1:
            pg.draw.lines(layer, (70, 90, 130, 200), False, self._px(np.array(self.path + [(self.X, self.Y)])), 3)

        # 历史脚印，越旧越淡
        for x, y, i, k0 in self.prints:
            age = (self.k - k0) / (len(self.gait_hist) * 2)
            alpha = int(200 * max(0.15, 1 - age))
            p = self._px([x, y])[0]
            pg.draw.circle(layer, (*LEG_RGB[i], alpha), p, 5)

        # ICR：转向中心。机身系里在 (−vy/ω, vx/ω)；太远就不画
        w_rad = np.radians(w)
        icr = None
        if abs(w) > 0.3:
            icr_b = np.array([-vy / w_rad, vx / w_rad])
            if np.hypot(*icr_b) < 900:
                icr = self._px(body_to_world(icr_b, self.X, self.Y, self.psi))[0]
                body = self._px([self.X, self.Y])[0]
                pg.draw.line(layer, (150, 90, 200, 120), body, icr, 1)
                pg.draw.line(layer, (150, 90, 200, 220), icr - (7, 7), icr + (7, 7), 2)
                pg.draw.line(layer, (150, 90, 200, 220), icr - (7, -7), icr + (7, -7), 2)
        scr.blit(layer, (0, 0))
        if icr is not None:
            scr.blit(self.font.render('ICR', True, (150, 90, 200)), icr + (9, -8))

        # 机身六边形 + 腿
        mount_w = body_to_world(MOUNT, self.X, self.Y, self.psi)
        hexagon = self._px(mount_w[HEX_ORDER])
        pg.draw.polygon(scr, (58, 66, 84), hexagon)
        nose = self._px(body_to_world(np.array([[150, 0], [95, 30], [95, -30]]), self.X, self.Y, self.psi))
        pg.draw.polygon(scr, (255, 200, 60), nose)                     # 黄三角 = 机头 (+x)
        for i in range(6):
            m_px = self._px(mount_w[i])[0]
            f_px = self._px(feet_w[i])[0]
            pg.draw.line(scr, LEG_RGB[i], m_px, f_px, 5)
            lift = max(0.0, feet[i, 2] - self.z0)
            if stance[i]:
                pg.draw.circle(scr, LEG_RGB[i], f_px, 8)
            else:                                                       # 摆动：空心圈，越高越大，带阴影
                pg.draw.circle(scr, (200, 203, 208), f_px, 6)
                pg.draw.circle(scr, LEG_RGB[i], f_px, int(8 + lift * 0.35), 3)
            scr.blit(self.font.render(LEG_NAMES[i], True, LEG_RGB[i]), f_px + (10, -20))

        # 重心投影
        com = self._px([self.X, self.Y])[0]
        pg.draw.circle(scr, (220, 50, 50), com, 5)

        # 速度箭头（世界系）
        v_w = body_to_world(np.array([vx, vy]), 0, 0, self.psi)
        if np.hypot(*v_w) > 0.5:
            tip = com + np.array([v_w[0], -v_w[1]]) * 3.0
            pg.draw.line(scr, (30, 120, 220), com, tip, 4)
            d = (tip - com) / np.linalg.norm(tip - com)
            n = np.array([-d[1], d[0]])
            pg.draw.polygon(scr, (30, 120, 220), [tip + d * 10, tip + n * 7, tip - n * 7])

        self._hud(cmd, rate_now, margin, stance)
        self._gait_strip()
        pg.display.flip()

    def _bar(self, x, y, label, val, vmax, unit, signed=True, warn=None):
        pg, scr = self.pg, self.screen
        W = 160
        pg.draw.rect(scr, (228, 231, 236), (x + 70, y + 3, W, 12), border_radius=3)
        frac = np.clip(val / vmax, -1, 1)
        col = (30, 120, 220) if warn is None or abs(val) < warn else (220, 70, 70)
        if signed:
            x0 = x + 70 + W / 2
            pg.draw.rect(scr, col, (min(x0, x0 + frac * W / 2), y + 3, abs(frac) * W / 2, 12), border_radius=3)
            pg.draw.line(scr, (150, 155, 165), (x0, y + 1), (x0, y + 17))
        else:
            pg.draw.rect(scr, col, (x + 70, y + 3, frac * W, 12), border_radius=3)
        scr.blit(self.font.render(label, True, (60, 66, 80)), (x, y))
        scr.blit(self.font.render(f'{val:6.1f} {unit}', True, (60, 66, 80)), (x + 78 + W, y))

    def _hud(self, cmd, rate_now, margin, stance):
        pg, scr = self.pg, self.screen
        panel = pg.Surface((370, 182), pg.SRCALPHA)
        panel.fill((255, 255, 255, 225))
        scr.blit(panel, (12, 12))
        x, y = 24, 20
        scr.blit(self.big.render(f'SIM   t = {self.k * self.dt:6.1f} s', True, (40, 44, 56)), (x, y))
        vx, vy, w = cmd
        self._bar(x, y + 32, 'vx', vx, self.v_max, 'mm/s')
        self._bar(x, y + 54, 'vy', vy, self.v_max, 'mm/s')
        self._bar(x, y + 76, 'w', w, self.w_max, 'deg/s')
        self._bar(x, y + 106, 'joint', rate_now, self.limit, 'deg/s', signed=False, warn=0.9 * self.limit)
        m_txt = 'n/a' if np.isnan(margin) else f'{margin:5.0f} mm'
        col = (40, 140, 80) if not np.isnan(margin) and margin > 30 else (210, 60, 60)
        scr.blit(self.font.render(f'margin {m_txt}   feet down {int(stance.sum())}', True, col), (x, y + 130))
        scr.blit(self.font.render(f'peak joint speed so far {self.peak:5.1f} deg/s', True, (90, 96, 110)), (x, y + 150))
        hint = self.font.render('B / Esc / close window = quit', True, (120, 126, 140))
        scr.blit(hint, (self.W - hint.get_width() - 14, 14))

    def _gait_strip(self):
        """底部滚动步态图：每行一条腿，实心 = 着地。最右边是现在。"""
        pg, scr = self.pg, self.screen
        n, rows = len(self.gait_hist), 6
        x0, h, W = 50, 11, self.W - 70
        y0 = self.H - rows * (h + 4) - 14
        panel = pg.Surface((self.W - 24, rows * (h + 4) + 16), pg.SRCALPHA)
        panel.fill((255, 255, 255, 225))
        scr.blit(panel, (12, y0 - 8))
        col_w = W / n
        for i in range(rows):
            y = y0 + i * (h + 4)
            scr.blit(self.font.render(LEG_NAMES[i], True, LEG_RGB[i]), (18, y - 3))
            run_start = None
            for k in range(n + 1):
                on = k < n and self.gait_hist[k, i]
                if on and run_start is None:
                    run_start = k
                if not on and run_start is not None:
                    pg.draw.rect(scr, LEG_RGB[i], (x0 + run_start * col_w, y, (k - run_start) * col_w, h))
                    run_start = None
        pg.draw.line(scr, (60, 66, 80), (x0 + W, y0 - 4), (x0 + W, y0 + rows * (h + 4)), 2)


# ---------------------------------------------------------------------------
# 2. KeyboardPad：没手柄时的替身（需要 LiveView 窗口在前台）
# ---------------------------------------------------------------------------
class KeyboardPad:
    """W/S = 前后，A/D = 左右平移，Q/E = 左转/右转，Esc = 退出。
    和 GamePad 一样做了组合上限和变化率限制，所以手感接近摇杆推满。"""

    def __init__(self, v_max=40, w_max=15, accel=100):
        import pygame
        self.pg = pygame
        pygame.init()
        self.v_max, self.w_max, self.accel = v_max, w_max, accel
        self.last = np.zeros(3)

    def read(self, dt=0.02):
        self.pg.event.pump()
        k = self.pg.key.get_pressed()
        raw = np.array([k[self.pg.K_w] - k[self.pg.K_s],
                        k[self.pg.K_a] - k[self.pg.K_d],
                        k[self.pg.K_q] - k[self.pg.K_e]], dtype=float)
        cmd = raw * np.array([self.v_max, self.v_max, self.w_max])
        lim = np.hypot(cmd[0], cmd[1]) / self.v_max + abs(cmd[2]) / self.w_max
        if lim > 1:
            cmd /= lim
        step = self.accel * dt * np.array([1, 1, self.w_max / self.v_max])
        self.last = self.last + np.clip(cmd - self.last, -step, step)
        return tuple(self.last)

    def quit_pressed(self):
        return bool(self.pg.key.get_pressed()[self.pg.K_ESCAPE])


# ---------------------------------------------------------------------------
# 3. replay：跑完以后看 log
# ---------------------------------------------------------------------------
def replay(path='teleop_log.npz', animate=True, every=2):
    """读 teleop.py 存的 log，画两张图：
       图 1 总览：世界俯视轨迹 / 命令 / 关节速度 / 稳定裕度 / 步态图
       图 2 3D 回放动画（世界系，镜头跟随）
    every: 动画每隔几帧画一次（2 = 25 fps，跑得动）。"""
    import matplotlib.pyplot as plt
    from matplotlib.animation import FuncAnimation
    from matplotlib.patches import Polygon
    from .fk import fk_matrix

    L = np.load(path, allow_pickle=True)
    t, cmd, feet, stance, thetas = L['t'], L['cmd'], L['feet'], L['stance'].astype(bool), L['thetas']
    rate = float(L['rate'])
    reason = str(L['reason'])
    N = len(t)
    if N < 2:
        print('log 里不到 2 帧，没什么可画的')
        return
    dt = 1 / rate
    pose = integrate_pose(cmd, dt)
    feet_w = np.stack([body_to_world(feet[k, :, :2], *pose[k]) for k in range(N)])
    ang = thetas.reshape(N, 6, 3)
    jrate = np.zeros_like(ang)
    jrate[1:] = np.abs(np.diff(ang, axis=0)) * rate
    margin = np.array([stability_margin(feet[k, stance[k], :2]) for k in range(N)])
    colors = [tuple(c / 255 for c in rgb) for rgb in LEG_RGB]
    failed = reason not in ('', 'quit')

    print(f'{path}: {N} 帧, {t[-1]:.1f} s, 结束原因: {reason or "正常退出"}')
    print(f'  最大关节速度 {jrate.max():.1f} °/s,  最小稳定裕度 {np.nanmin(margin):.1f} mm,'
          f'  走了 {np.hypot(*pose[-1, :2]):.0f} mm,  转了 {np.degrees(pose[-1, 2]):.0f}°')

    # ---------------- 图 1：总览 ----------------
    fig = plt.figure(figsize=(14, 8.5))
    gs = fig.add_gridspec(4, 2, width_ratios=[1.1, 1], height_ratios=[1, 1, 1, 0.8], hspace=0.55, wspace=0.22)
    fig.suptitle(f'teleop log  ·  {L["gait"]}  T={float(L["T"])} s  h={float(L["H"])} mm  ·  '
                 f'{"SIM" if bool(L["sim"]) else "REAL"}  ·  {t[-1]:.1f} s', fontsize=13)

    ax = fig.add_subplot(gs[:, 0])
    for i in range(6):
        down = stance[:, i] & ~np.r_[True, stance[:-1, i]]            # 落地那一帧
        ax.plot(feet_w[down, i, 0], feet_w[down, i, 1], 'o', ms=4, color=colors[i], alpha=0.6, label=LEG_NAMES[i])
    sc = ax.scatter(pose[:, 0], pose[:, 1], c=t, cmap='viridis', s=3, zorder=3)
    fig.colorbar(sc, ax=ax, fraction=0.04, pad=0.02, label='t (s)')
    for k in np.linspace(0, N - 1, 6).astype(int):                     # 几个时刻的机身轮廓
        hexw = body_to_world(MOUNT[HEX_ORDER], *pose[k])
        ax.add_patch(Polygon(hexw, closed=True, fc='0.3', alpha=0.25, ec='0.2'))
        nose = body_to_world(np.array([[130, 0]]), *pose[k])[0]
        ax.annotate('', nose, pose[k, :2], arrowprops=dict(arrowstyle='->', color='0.2'))
    if failed:
        ax.plot(*pose[-1, :2], 'rx', ms=14, mew=3)
    ax.set_aspect('equal')
    ax.set_xlabel('world x (mm)')
    ax.set_ylabel('world y (mm)')
    ax.set_title('Top view: body path (color = time) and footprints')
    ax.legend(ncol=6, fontsize=8, loc='upper left')
    ax.grid(alpha=0.3)

    def mark_end(a):
        if failed:
            a.axvline(t[-1], color='r', lw=1.5)

    a1 = fig.add_subplot(gs[0, 1])
    a1.plot(t, cmd[:, 0], label='vx (mm/s)')
    a1.plot(t, cmd[:, 1], label='vy (mm/s)')
    a1.plot(t, cmd[:, 2], label='w (°/s)')
    a1.set_title('Commands from the stick')
    a1.legend(fontsize=8, ncol=3, loc='upper right')
    mark_end(a1)

    a2 = fig.add_subplot(gs[1, 1], sharex=a1)
    for j, name in enumerate(['coxa', 'femur', 'tibia']):
        a2.plot(t, jrate[:, :, j].max(axis=1), lw=1, label=name)
    a2.axhline(100, color='r', ls='--', lw=1)
    a2.set_ylabel('°/s')
    a2.set_title('Fastest joint of each type (limit 100 °/s)')
    a2.legend(fontsize=8, ncol=3, loc='upper right')
    mark_end(a2)

    a3 = fig.add_subplot(gs[2, 1], sharex=a1)
    a3.plot(t, margin, 'g', lw=1)
    a3.axhline(0, color='r', lw=1)
    a3.set_ylabel('mm')
    a3.set_title('Static stability margin')
    a3b = a3.twinx()
    a3b.step(t, stance.sum(axis=1), color='0.6', lw=0.8, where='post')
    a3b.set_ylim(0, 7)
    a3b.set_ylabel('feet down', color='0.5')
    mark_end(a3)

    a4 = fig.add_subplot(gs[3, 1], sharex=a1)
    for i in range(6):
        on = stance[:, i]
        edges = np.flatnonzero(np.diff(np.r_[0, on.astype(int), 0]))
        a4.broken_barh([(t[s0], t[min(s1, N - 1)] - t[s0]) for s0, s1 in zip(edges[::2], edges[1::2])],
                       (5 - i - 0.4, 0.8), color=colors[i])
    a4.set_yticks(range(6))
    a4.set_yticklabels(LEG_NAMES[::-1])
    a4.set_xlabel('t (s)')
    a4.set_title('Gait diagram (bar = foot on ground)')
    mark_end(a4)
    if failed:
        fig.text(0.5, 0.005, f'stopped at t={t[-1]:.2f}s: {reason}', color='r', ha='center')

    # ---------------- 图 2：3D 回放 ----------------
    anim = None
    if animate:
        z_ground = feet[:, :, 2].min()

        def leg_points(k):
            """(6, 4, 3)：coxa、femur 关节、膝、脚尖，世界系。"""
            out = np.zeros((6, 4, 3))
            c, s = np.cos(pose[k, 2]), np.sin(pose[k, 2])
            Rw = np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])
            for i in range(6):
                toe, knee, femur = fk_matrix([ang[k, i, 0]], [ang[k, i, 1]], [ang[k, i, 2]])
                pts = np.vstack([np.zeros(3), femur[0], knee[0], toe[0]])
                ca, sa = np.cos(np.radians(ALPHA[i])), np.sin(np.radians(ALPHA[i]))
                Ra = np.array([[ca, -sa, 0], [sa, ca, 0], [0, 0, 1]])
                pts = pts @ Ra.T + np.array([MOUNT[i][0], MOUNT[i][1], 0])
                out[i] = pts @ Rw.T + np.array([pose[k, 0], pose[k, 1], 0])
            return out

        fig3 = plt.figure(figsize=(10, 7.5))
        ax3 = fig3.add_subplot(projection='3d')
        body_line, = ax3.plot([], [], [], 'k-', lw=3)
        nose_line, = ax3.plot([], [], [], '-', color='orange', lw=3)
        leg_lines = [ax3.plot([], [], [], '-', color=colors[i], lw=2.5)[0] for i in range(6)]
        toes = [ax3.plot([], [], [], 'o', color=colors[i], ms=7)[0] for i in range(6)]
        support, = ax3.plot([], [], [], 'g-', lw=1.5)
        trail, = ax3.plot([], [], [], '-', color='0.4', lw=1)
        prints, = ax3.plot([], [], [], 'k.', ms=3, alpha=0.35)
        label = ax3.text2D(0.02, 0.95, '', transform=ax3.transAxes)
        ax3.set_xlabel('x (mm)')
        ax3.set_ylabel('y (mm)')
        ax3.set_zlabel('z (mm)')
        ax3.view_init(elev=28, azim=-125)
        down_mask = stance & ~np.vstack([np.ones((1, 6), bool), stance[:-1]])

        def update(k):
            P = leg_points(k)
            coxa = P[:, 0, :]
            ring = coxa[HEX_ORDER + [HEX_ORDER[0]]]
            body_line.set_data_3d(ring[:, 0], ring[:, 1], ring[:, 2])
            nose = body_to_world(np.array([[0, 0], [130, 0]]), *pose[k])
            nose_line.set_data_3d(nose[:, 0], nose[:, 1], [0, 0])
            for i in range(6):
                leg_lines[i].set_data_3d(P[i, :, 0], P[i, :, 1], P[i, :, 2])
                toes[i].set_data_3d([P[i, 3, 0]], [P[i, 3, 1]], [P[i, 3, 2]])
                toes[i].set_markerfacecolor(colors[i] if stance[k, i] else 'white')
            S = support_polygon(feet_w[k, stance[k]])
            if S is not None:
                S = np.vstack([S, S[:1]])
                support.set_data_3d(S[:, 0], S[:, 1], np.full(len(S), z_ground))
            trail.set_data_3d(pose[:k + 1, 0], pose[:k + 1, 1], np.full(k + 1, z_ground))
            fp = feet_w[:k + 1][down_mask[:k + 1]]
            prints.set_data_3d(fp[:, 0], fp[:, 1], np.full(len(fp), z_ground))
            cx, cy = pose[k, :2]
            ax3.set_xlim(cx - 320, cx + 320)
            ax3.set_ylim(cy - 320, cy + 320)
            ax3.set_zlim(z_ground - 10, z_ground + 240)
            ax3.set_box_aspect((640, 640, 250))
            vx, vy, w = cmd[k]
            label.set_text(f't = {t[k]:5.2f} s   v = ({vx:4.0f}, {vy:4.0f}) mm/s   w = {w:4.1f} °/s   '
                           f'margin = {margin[k]:4.0f} mm')
            return []

        anim = FuncAnimation(fig3, update, frames=range(0, N, every), interval=1000 * every / rate)
        # 想存成视频：anim.save('teleop.gif', fps=rate / every)   （需要 pillow）

    plt.show()
    return anim


if __name__ == '__main__':
    replay(sys.argv[1] if len(sys.argv) > 1 else 'teleop_log.npz')
