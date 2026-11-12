import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation
from matplotlib.patches import Polygon

from utils.planner import make_plan_feet
from utils.feet_traj import feet_straight
from utils.gaits import leg_phase, GAITS
from utils.body_ik import body_ik, a as ALPHA, m as MOUNT
from utils.fk import fk_matrix

# ---------------------------------------------------------------------------
# Sean's original quick plot (kept for reference)
# ---------------------------------------------------------------------------
# feet_fn = lambda t: feet_straight(t, T=2.5, S=60, h=30, gait='tripod')
# times, thetas = make_plan_feet(feet_fn, duration=3)
#
# plt.figure()
# plt.plot(times, thetas[:, 0:4])  # Matplotlib automatically plots each column as a separate line
# plt.xlabel("Time")
# plt.ylabel("Outputs")
# plt.title("All 18 Outputs Over Time")
# plt.show()

# ---------------------------------------------------------------------------
# Parameters: change these and re-run
# ---------------------------------------------------------------------------
GAIT = 'tripod'      # 'tripod' / 'ripple' / 'wave'
T = 2.5              # period, s
S = 60               # stroke, mm
H = 30               # step height, mm
CYCLES = 2           # how many periods to simulate
RATE = 50            # Hz, same as the serial link
SPEED_LIMIT = 100    # deg/s, same as the planner check
SHOW_ANIMATION = True

LEG_NAMES = ['R1', 'R2', 'R3', 'L1', 'L2', 'L3']
LEG_COLORS = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
JOINT_NAMES = ['coxa θ1', 'femur θ2', 'tibia θ3']
JOINT_LIMITS = [(-45, 45), (-75, 75), (15, 165)]

# ---------------------------------------------------------------------------
# 1. Plan (same plan that walk_run.py will send)
# ---------------------------------------------------------------------------
duration = CYCLES * T
feet_fn = lambda t: feet_straight(t, T=T, S=S, h=H, gait=GAIT)
times, thetas = make_plan_feet(feet_fn, duration=duration, rate=RATE)
N = len(times)
beta = GAITS[GAIT][0]
v = S / (beta * T)  # body speed, mm/s

# Sanity check: the plan's angles must match feet_fn evaluated at the same time
k_chk = min(10, N - 1)
th_chk, _ = body_ik(np.zeros(6), feet_fn(times[k_chk]))
if not np.allclose(th_chk.flatten(), thetas[k_chk], atol=1e-6):
    print("WARNING: plan angles do not match feet_fn(times[k]). "
          "Check that make_plan_feet calls feet_fn(times[i]), not feet_fn(i).")

# ---------------------------------------------------------------------------
# 2. Everything we want to look at, computed once
# ---------------------------------------------------------------------------
feet_B = np.array([feet_fn(t) for t in times])                    # (N, 6, 3) body frame
stance = np.array([[leg_phase(i, t, T, GAIT)[0] for i in range(6)] for t in times])  # (N, 6)
body_x = v * times                                                 # body position in world, mm
feet_W = feet_B.copy()
feet_W[:, :, 0] += body_x[:, None]                                 # world frame (body moves along +x)

ang = thetas.reshape(N, 6, 3)                                      # (N, leg, joint)
rate = np.zeros_like(ang)
rate[1:] = np.diff(ang, axis=0) * RATE                             # deg/s


def stability_margin(pts):
    """Signed distance from the origin (CoM projection) to the nearest edge
    of the support polygon. pts: (n, 2) stance feet in the body frame."""
    if len(pts) < 3:
        return np.nan
    c = pts.mean(axis=0)
    order = np.argsort(np.arctan2(pts[:, 1] - c[1], pts[:, 0] - c[0]))
    P = pts[order]                                                 # counter-clockwise
    d = []
    for k in range(len(P)):
        p, q = P[k], P[(k + 1) % len(P)]
        e = q - p
        n_in = np.array([-e[1], e[0]]) / np.linalg.norm(e)         # inward normal for CCW
        d.append(np.dot(-p, n_in))                                 # >0 means origin is inside
    return min(d)


margin = np.array([stability_margin(feet_B[k, stance[k], :2]) for k in range(N)])
n_down = stance.sum(axis=1)

# Slip check: during one stance phase a foot must not move in the world frame
slip = 0.0
for i in range(6):
    k = 0
    while k < N:
        if stance[k, i]:
            k0 = k
            while k < N and stance[k, i]:
                k += 1
            seg = feet_W[k0:k, i, :]
            slip = max(slip, np.abs(seg - seg[0]).max())
        else:
            k += 1

# ---------------------------------------------------------------------------
# 3. Summary in the terminal
# ---------------------------------------------------------------------------
print(f"gait={GAIT}  T={T}s  S={S}mm  h={H}mm  beta={beta:.3f}")
print(f"body speed v = {v:.1f} mm/s, distance in {duration:.1f}s = {v * duration:.0f} mm")
peak = np.abs(rate).max(axis=(0, 1))
for j in range(3):
    print(f"peak |{JOINT_NAMES[j]}| speed = {peak[j]:6.1f} deg/s (limit {SPEED_LIMIT})")
print(f"feet on ground: min {n_down.min()}, max {n_down.max()}")
print(f"static stability margin: min {np.nanmin(margin):.1f} mm")
print(f"stance-foot slip in world frame: max {slip:.2e} mm  (should be ~0)")

# ---------------------------------------------------------------------------
# 4. Dashboard (static)
# ---------------------------------------------------------------------------
fig = plt.figure(figsize=(15, 11), constrained_layout=True)
fig.suptitle(f"{GAIT}  T={T}s  S={S}mm  h={H}mm   v={v:.1f} mm/s", fontsize=14)
gs = fig.add_gridspec(3, 2, height_ratios=[1, 1.4, 1.3])

# 4a. Gait diagram: dark = stance, light = swing
ax = fig.add_subplot(gs[0, 0])
rows = ['L1', 'L2', 'L3', 'R1', 'R2', 'R3']                         # same layout as the worksheet
for r, name in enumerate(rows):
    i = LEG_NAMES.index(name)
    col = stance[:, i]
    k = 0
    while k < N:
        k0 = k
        while k < N and col[k] == col[k0]:
            k += 1
        t0, t1 = times[k0], times[k - 1] + 1 / RATE
        ax.broken_barh([(t0, t1 - t0)], (r - 0.4, 0.8),
                       facecolors=LEG_COLORS[i] if col[k0] else 'white',
                       edgecolors=LEG_COLORS[i], alpha=0.85 if col[k0] else 1)
ax.set_yticks(range(6))
ax.set_yticklabels(rows)
ax.invert_yaxis()
ax.axhline(2.5, color='k', lw=0.8)
ax.set_xlim(0, duration)
ax.set_xlabel('time (s)')
ax.set_title('Gait diagram (filled = stance, empty = swing)')

# 4b. Stability margin + number of feet down
ax = fig.add_subplot(gs[0, 1])
ax.plot(times, margin, color='k', lw=1.5, label='stability margin')
kmin = np.nanargmin(margin)
ax.plot(times[kmin], margin[kmin], 'ro')
ax.annotate(f"min {margin[kmin]:.1f} mm", (times[kmin], margin[kmin]),
            textcoords='offset points', xytext=(8, -14), color='r')
ax.set_ylim(0, max(160, np.nanmax(margin) + 10))
ax.set_ylabel('margin (mm)')
ax.set_xlabel('time (s)')
ax.set_xlim(0, duration)
ax2 = ax.twinx()
ax2.step(times, n_down, where='post', color='tab:gray', alpha=0.6)
ax2.set_ylim(0, 7)
ax2.set_ylabel('feet on ground', color='tab:gray')
ax.set_title('Static stability')

# 4c. Joint angles: one panel per joint type, one line per leg, limits shaded
sub = gs[1, 0].subgridspec(3, 1, hspace=0.05)
for j in range(3):
    ax = fig.add_subplot(sub[j])
    for i in range(6):
        ax.plot(times, ang[:, i, j], color=LEG_COLORS[i], lw=1.3, label=LEG_NAMES[i])
    lo, hi = JOINT_LIMITS[j]
    ax.axhspan(hi, hi + 30, color='r', alpha=0.08)
    ax.axhspan(lo - 30, lo, color='r', alpha=0.08)
    ymin, ymax = ang[:, :, j].min(), ang[:, :, j].max()
    ax.set_ylim(min(ymin - 5, lo - 2) if ymin - 5 < lo else ymin - 5,
                max(ymax + 5, hi + 2) if ymax + 5 > hi else ymax + 5)
    ax.set_ylabel(f'{JOINT_NAMES[j]} (°)')
    ax.set_xlim(0, duration)
    if j == 0:
        ax.set_title('Joint angles (red band = beyond limit)')
        ax.legend(ncol=6, fontsize=8, loc='upper right')
    if j < 2:
        ax.tick_params(labelbottom=False)
    else:
        ax.set_xlabel('time (s)')

# 4d. Joint speeds: worst leg per joint type, against the limit
ax = fig.add_subplot(gs[1, 1])
for j, c in zip(range(3), ['tab:blue', 'tab:orange', 'tab:green']):
    ax.plot(times, np.abs(rate[:, :, j]).max(axis=1), color=c, lw=1.3,
            label=f'{JOINT_NAMES[j]} (peak {peak[j]:.0f})')
ax.axhline(SPEED_LIMIT, color='r', ls='--', lw=1.2, label=f'limit {SPEED_LIMIT}°/s')
ax.set_xlim(0, duration)
ax.set_ylim(0, max(SPEED_LIMIT * 1.2, peak.max() * 1.1))
ax.set_xlabel('time (s)')
ax.set_ylabel('|joint speed| (deg/s), worst leg')
ax.legend(fontsize=9, loc='upper right')
ax.set_title('Joint speed vs limit')

# 4e. Foot loops in the body frame, side view (x vs z). Left and right legs at the
#     same x share the same loop shape (they only differ in phase), so they overlap.
ax = fig.add_subplot(gs[2, 0])
for i in range(6):
    st = stance[:, i]
    ax.plot(feet_B[~st, i, 0], feet_B[~st, i, 2], '.', ms=3, color=LEG_COLORS[i])
    ax.plot(feet_B[st, i, 0], feet_B[st, i, 2], '.', ms=3, color='k')
for x0, txt in [(225.5, 'front legs R1/L1'), (0, 'middle legs R2/L2'), (-225.5, 'rear legs R3/L3')]:
    ax.text(x0, feet_B[:, :, 2].min() + H + 12, txt, ha='center', fontsize=9)
ax.axhline(feet_B[:, :, 2].min(), color='0.6', lw=0.8)
ax.set_xlim(-300, 300)
ax.set_ylim(feet_B[:, :, 2].min() - 10, feet_B[:, :, 2].min() + H + 25)
ax.set_xlabel('body x (mm), front →')
ax.set_ylabel('body z (mm)')
ax.set_title('Foot loops, body frame side view (black = stance, color = swing)')

# 4f. Top view in the world: footprints and body path
ax = fig.add_subplot(gs[2, 1])
for i in range(6):
    st = stance[:, i]
    # one footprint per stance phase
    starts = np.where(st & ~np.r_[False, st[:-1]])[0]
    ax.plot(feet_W[starts, i, 0], feet_W[starts, i, 1], 'o', color=LEG_COLORS[i], ms=7,
            label=LEG_NAMES[i])
    ax.plot(feet_W[~st, i, 0], feet_W[~st, i, 1], '-', color=LEG_COLORS[i], lw=0.8, alpha=0.5)
ax.plot(body_x, np.zeros(N), 'k--', lw=1, label='body path')
# support polygon at the moment of minimum margin
kk = kmin
P = feet_W[kk, stance[kk], :2]
if len(P) >= 3:
    c = P.mean(axis=0)
    P = P[np.argsort(np.arctan2(P[:, 1] - c[1], P[:, 0] - c[0]))]
    ax.add_patch(Polygon(P, closed=True, fc='g', alpha=0.15, ec='g'))
    ax.plot(body_x[kk], 0, 'r+', ms=12, mew=2)
    ax.annotate(f'support polygon at t={times[kk]:.2f}s (min margin)', (body_x[kk], 0),
                textcoords='offset points', xytext=(10, 10), fontsize=8, color='g')
ax.set_aspect('equal')
ax.set_xlabel('world x (mm), walking direction →')
ax.set_ylabel('world y (mm)')
ax.legend(ncol=4, fontsize=8, loc='upper left')
ax.set_title(f'Footprints in the world (stride λ = {S / beta:.0f} mm)')

# ---------------------------------------------------------------------------
# 5. Animation: the robot walking in 3D (world frame)
# ---------------------------------------------------------------------------
def leg_points(k):
    """(6, 4, 3): coxa axis, femur joint, knee, toe for every leg, world frame, frame k."""
    out = np.zeros((6, 4, 3))
    for i in range(6):
        t1, t2, t3 = ang[k, i]
        toe, knee, femur = fk_matrix([t1], [t2], [t3])
        pts_L = np.vstack([np.zeros(3), femur[0], knee[0], toe[0]])
        ca, sa = np.cos(np.radians(ALPHA[i])), np.sin(np.radians(ALPHA[i]))
        R = np.array([[ca, -sa, 0], [sa, ca, 0], [0, 0, 1]])
        pts_B = pts_L @ R.T + np.array([MOUNT[i][0], MOUNT[i][1], 0])
        pts_B[:, 0] += body_x[k]
        out[i] = pts_B
    return out


if SHOW_ANIMATION:
    LEGS = np.array([leg_points(k) for k in range(N)])            # (N, 6, 4, 3)
    ground_z = feet_B[:, :, 2].min()
    hex_idx = [0, 1, 2, 5, 4, 3, 0]                                # R1 R2 R3 L3 L2 L1 around the body

    fig3 = plt.figure(figsize=(10, 7))
    ax3 = fig3.add_subplot(projection='3d')
    body_line, = ax3.plot([], [], [], 'k-', lw=2.5)
    leg_lines = [ax3.plot([], [], [], '-', color=LEG_COLORS[i], lw=2.5)[0] for i in range(6)]
    toe_dots = [ax3.plot([], [], [], 'o', color=LEG_COLORS[i], ms=7)[0] for i in range(6)]
    prints = ax3.plot([], [], [], 'k.', ms=3, alpha=0.4)[0]
    support = ax3.plot([], [], [], 'g-', lw=1.5)[0]
    gx, gy = np.meshgrid(np.linspace(-300, body_x[-1] + 300, 2), np.linspace(-300, 300, 2))
    ax3.plot_surface(gx, gy, np.full_like(gx, ground_z), color='0.85', alpha=0.3)
    label = ax3.text2D(0.02, 0.95, '', transform=ax3.transAxes)
    ax3.set_xlabel('x (mm)')
    ax3.set_ylabel('y (mm)')
    ax3.set_zlabel('z (mm)')
    ax3.view_init(elev=28, azim=-125)

    def update(k):
        L = LEGS[k]
        coxa = L[:, 0, :]
        body_line.set_data_3d(coxa[hex_idx, 0], coxa[hex_idx, 1], coxa[hex_idx, 2])
        for i in range(6):
            leg_lines[i].set_data_3d(L[i, :, 0], L[i, :, 1], L[i, :, 2])
            toe_dots[i].set_data_3d([L[i, 3, 0]], [L[i, 3, 1]], [L[i, 3, 2]])
            toe_dots[i].set_markerfacecolor(LEG_COLORS[i] if stance[k, i] else 'white')
        past = feet_W[:k + 1][stance[:k + 1]]
        prints.set_data_3d(past[:, 0], past[:, 1], past[:, 2])
        P = feet_W[k, stance[k], :2]
        if len(P) >= 3:
            c = P.mean(axis=0)
            P = P[np.argsort(np.arctan2(P[:, 1] - c[1], P[:, 0] - c[0]))]
            P = np.vstack([P, P[:1]])
            support.set_data_3d(P[:, 0], P[:, 1], np.full(len(P), ground_z))
        cx = body_x[k]
        ax3.set_xlim(cx - 300, cx + 300)
        ax3.set_ylim(-300, 300)
        ax3.set_zlim(ground_z - 10, ground_z + 250)
        ax3.set_box_aspect((600, 600, 260))
        label.set_text(f't = {times[k]:.2f} s   feet down = {n_down[k]}   margin = {margin[k]:.0f} mm')
        return [body_line, *leg_lines, *toe_dots, prints, support, label]

    anim = FuncAnimation(fig3, update, frames=N, interval=1000 / RATE, blit=False)
    # To save a video: anim.save('walk.gif', fps=RATE)   (needs pillow)

plt.show()
