import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium", app_title="HexPod Academy · Stage 3 IK")


@app.cell(hide_code=True)
def _():
    import marimo as mo
    import numpy as np
    import json
    import sys
    IN_BROWSER = sys.platform == "emscripten"
    return IN_BROWSER, json, mo, np


@app.cell(hide_code=True)
def _(mo):
    _q = mo.query_params().get("lang")
    lang = mo.ui.dropdown(options={"English": "en", "中文": "zh"},
                          value="中文" if _q == "zh" else "English", label="🌐")
    return (lang,)


@app.cell(hide_code=True)
def _(TEXT, lang):
    def t(key):
        return TEXT.get(lang.value, TEXT["en"]).get(key, TEXT["en"].get(key, key))
    return (t,)


@app.cell(hide_code=True)
def _(lang, mo, progress, t):
    mo.vstack([
        mo.hstack([mo.md(f"**HexPod Academy** · {t('crumb')}"), lang], justify="space-between", align="center"),
        mo.md(t("intro")),
        progress,
    ])
    return


@app.cell(hide_code=True)
def _(mo, ok1, ok2, ok3, ok4, ok5, t):
    _steps = [ok1, ok2, ok3, ok4, ok5]
    _names = ["θ1", "(u, z)", "θ3", "θ2", t("roundtrip")]
    _chips = " ".join(
        f"<span style='display:inline-block;padding:2px 10px;margin:2px;border-radius:99px;"
        f"background:{'#2b8a5733' if s else '#8882'};font-family:monospace;font-size:13px'>"
        f"{'✓' if s else '○'} {i + 1} · {n}</span>" for i, (s, n) in enumerate(zip(_steps, _names)))
    _done = sum(_steps)
    _reward = ("🏆 " + t("all_unlocked")) if _done == 5 else ("🔒 " + t("locked_n").format(n=5 - _done))
    progress = mo.md(f"{_chips}<br><span style='font-size:14px'>{_reward}</span>")
    return (progress,)


@app.cell(hide_code=True)
def _(mo, t):
    mo.md(t("given_md"))
    return


@app.cell
def _(np):
    # ── Given (from Stage 1) — you don't need to change anything here ──
    L1, L2, L3 = 62.0, 76.0, 132.0           # coxa, femur, tibia (mm)
    LIMITS = {"theta1": (-45, 45), "theta2": (-75, 75), "theta3": (15, 165)}  # degrees

    def fk(theta1, theta2, theta3):
        """Joint angles (deg) -> foot position (x, y, z) in mm, leg frame."""
        t1, t2, t23 = np.radians(theta1), np.radians(theta2), np.radians(np.subtract(theta2, theta3))
        r = L1 + L2 * np.cos(t2) + L3 * np.cos(t23)
        z = L2 * np.sin(t2) + L3 * np.sin(t23)
        return np.array([r * np.cos(t1), r * np.sin(t1), z])

    fk(0, 30, 105)   # standing pose -> about (162, 0, -89.5)
    return L1, L2, L3, LIMITS, fk


@app.cell(hide_code=True)
def _(mo, t):
    mo.vstack([mo.md(t("ex1_md")), mo.accordion({t("hint") + " 1": mo.md(t("ex1_h1")), t("hint") + " 2": mo.md(t("ex1_h2")), t("answer"): mo.md(t("ex1_a"))})])
    return


@app.cell
def _(np):
    def solve_theta1(x, y):
        """Coxa angle in DEGREES: the direction from the coxa joint to (x, y)."""
        # (reference solution)
        return np.degrees(np.arctan2(y, x))
    return (solve_theta1,)


@app.cell(hide_code=True)
def _(check, solve_theta1):
    ok1, _view = check(
        solve_theta1,
        [((162, 0), 0.0), ((100, 100), 45.0), ((100, -100), -45.0), ((0, 150), 90.0),
         ((-50, -50), -135.0), ((120, 30), 14.0362)],
        tol=0.01, radians_hint=True)
    _view
    return (ok1,)


@app.cell(hide_code=True)
def _(mo, t):
    mo.vstack([mo.md(t("ex2_md")), mo.accordion({t("hint") + " 1": mo.md(t("ex2_h1")), t("answer"): mo.md(t("ex2_a"))})])
    return


@app.cell
def _(L1, np):
    def to_leg_plane(x, y, z):
        """Return (u, z): horizontal distance from the FEMUR joint to the target, and height."""
        # (reference solution)
        r = np.hypot(x, y)
        return r - L1, z
    return (to_leg_plane,)


@app.cell(hide_code=True)
def _(check, to_leg_plane):
    ok2, _view = check(
        to_leg_plane,
        [((162, 0, -89.5), (100.0, -89.5)), ((100, 100, -89.5), (79.4214, -89.5)),
         ((62, 0, 50), (0.0, 50.0)), ((150, -80, -120), (108.0, -120.0)), ((0, 200, -30), (138.0, -30.0))],
        tol=0.01)
    _view
    return (ok2,)


@app.cell(hide_code=True)
def _(mo, t):
    mo.vstack([mo.md(t("ex3_md")), mo.accordion({t("hint") + " 1": mo.md(t("ex3_h1")), t("hint") + " 2": mo.md(t("ex3_h2")), t("answer"): mo.md(t("ex3_a"))})])
    return


@app.cell
def _(L2, L3, np):
    def solve_theta3(u, z):
        """Knee angle in DEGREES (knee-up, so positive). Return None if (u, z) is out of reach."""
        # (reference solution)
        D = np.hypot(u, z)
        c = (D**2 - L2**2 - L3**2) / (2 * L2 * L3)
        if abs(c) > 1:
            return None
        return np.degrees(np.arccos(c))
    return (solve_theta3,)


@app.cell(hide_code=True)
def _(check, solve_theta3):
    ok3, _view = check(
        solve_theta3,
        [((100, -89.5), 104.9906), ((150, -50), 84.8529), ((0, -150), 91.9994), ((60, 20), 163.1245),
         ((300, 0), None), ((20, 10), None), ((207.99, 0), 1.1668)],
        tol=0.01, radians_hint=True)
    _view
    return (ok3,)


@app.cell(hide_code=True)
def _(mo, t):
    mo.vstack([mo.md(t("ex4_md")), mo.accordion({t("hint") + " 1": mo.md(t("ex4_h1")), t("hint") + " 2": mo.md(t("ex4_h2")), t("answer"): mo.md(t("ex4_a"))})])
    return


@app.cell
def _(L2, L3, np):
    def solve_theta2(u, z, theta3):
        """Femur angle in DEGREES, measured up from horizontal. Keep it in [-180, 180]."""
        # (reference solution)
        t3 = np.radians(theta3)
        alpha = np.arctan2(z, u)
        beta = np.arctan2(L3 * np.sin(t3), L2 + L3 * np.cos(t3))
        v = np.degrees(alpha + beta)
        return (v + 180) % 360 - 180
    return (solve_theta2,)


@app.cell(hide_code=True)
def _(check, solve_theta2):
    ok4, _view = check(
        solve_theta2,
        [((100, -89.5, 104.9906), 29.9981), ((150, -50, 84.8529), 37.8156), ((0, -150, 91.9994), -28.4222),
         ((60, 20, 163.1245), 161.1434), ((-100, 10, 130.7614), -89.8945)],
        tol=0.01, radians_hint=True)
    _view
    return (ok4,)


@app.cell(hide_code=True)
def _(mo, t):
    mo.md(t("ex5_md"))
    return


@app.cell
def _(LIMITS, np, solve_theta1, solve_theta2, solve_theta3, to_leg_plane):
    def within_limits(theta1, theta2, theta3):
        eps = 1e-9
        return all(lo - eps <= v <= hi + eps for v, (lo, hi) in zip((theta1, theta2, theta3), LIMITS.values()))

    def ik(x, y, z):
        """Foot target (mm, leg frame) -> np.array([theta1, theta2, theta3]) in degrees, or None."""
        theta1 = solve_theta1(x, y)
        u, zz = to_leg_plane(x, y, z)
        theta3 = solve_theta3(u, zz)
        if theta3 is None:
            return None
        theta2 = solve_theta2(u, zz, theta3)
        if not within_limits(theta1, theta2, theta3):
            return None
        return np.array([theta1, theta2, theta3], dtype=float)
    return (ik,)


@app.cell(hide_code=True)
def _(LIMITS, fk, ik, mo, np, ok1, ok2, ok3, ok4, t):
    def _roundtrip():
        if not (ok1 and ok2 and ok3 and ok4):
            return False, mo.callout(mo.md(t("rt_wait")), kind="neutral")
        _rng = np.random.default_rng(3)
        _n, _worst, _fails = 500, 0.0, []
        _tested = 0
        while _tested < _n:
            _a = [_rng.uniform(*LIMITS[k]) for k in ("theta1", "theta2", "theta3")]
            _p = fk(*_a)
            if np.hypot(_p[0], _p[1]) * np.sign(_p[0]) < 1:   # foot folded behind the coxa: see "Going further"
                continue
            _tested += 1
            try:
                _s = ik(*_p)
            except Exception as e:
                _fails.append((_p, f"error: {e}")); continue
            if _s is None:
                _fails.append((_p, "None")); continue
            _err = float(np.linalg.norm(fk(*_s) - _p))
            _worst = max(_worst, _err)
            if _err > 1e-6:
                _fails.append((_p, f"{_err:.3g} mm off"))
        _far = [ik(400, 0, 0), ik(70, 0, 0), ik(100, 150, -90)]
        _good = _n - len(_fails)
        _ok = not _fails and all(v is None for v in _far)
        _lines = [t("rt_score").format(good=_good, n=_n, worst=_worst)]
        if any(v is not None for v in _far):
            _lines.append(t("rt_far"))
        for _p, _why in _fails[:3]:
            _lines.append(f"- ✗ target ({_p[0]:.1f}, {_p[1]:.1f}, {_p[2]:.1f}) → {_why}")
        return _ok, mo.callout(mo.md(("🎉 " + t("rt_pass") + "\n\n" if _ok else "") + "\n".join(_lines)), kind="success" if _ok else "danger")

    ok5, _view = _roundtrip()
    _view
    return (ok5,)


@app.cell(hide_code=True)
def _(mo, t):
    sx = mo.ui.slider(60, 260, value=162, step=1, label="x (mm)", show_value=True)
    sy = mo.ui.slider(-150, 150, value=0, step=1, label="y (mm)", show_value=True)
    sz = mo.ui.slider(-200, 80, value=-89.5, step=0.5, label="z (mm)", show_value=True)
    mo.vstack([mo.md(t("play_md")), mo.hstack([sx, sy, sz], wrap=True)])
    return sx, sy, sz


@app.cell(hide_code=True)
def _(L1, L2, L3, ik, mo, np, ok4, sx, sy, sz, t):
    def _svg(x, y, z, ang):
        W, H, s = 640, 300, 0.95
        def side(u, zz): return 150 + u * s, 150 - zz * s
        def top(xx, yy): return 470 + xx * 0.55 - 60, 150 - yy * 0.55
        out = [f"<svg viewBox='0 0 {W} {H}' style='width:100%;max-width:640px;font-family:monospace;font-size:12px'>",
               "<rect x='0' y='0' width='380' height='300' fill='#8881'/><rect x='390' y='0' width='250' height='300' fill='#8881'/>",
               "<text x='8' y='16' fill='currentColor'>side (u, z)</text><text x='398' y='16' fill='currentColor'>top (x, y)</text>"]
        cx, cy = side(0, 0)
        out.append(f"<circle cx='{cx}' cy='{cy}' r='{(L2 + L3) * s}' fill='#2a6fb022'/><circle cx='{cx}' cy='{cy}' r='{(L3 - L2) * s}' fill='#ffffff'/>")
        r = np.hypot(x, y); u = r - L1
        tx, ty = side(u, z)
        out.append(f"<circle cx='{tx}' cy='{ty}' r='7' fill='none' stroke='#d9771f' stroke-width='2'/>")
        ox, oy = top(0, 0); px, py = top(x, y)
        out.append(f"<circle cx='{px}' cy='{py}' r='6' fill='none' stroke='#d9771f' stroke-width='2'/>")
        if ang is not None:
            t1, t2, t3 = np.radians(ang)
            k = (L2 * np.cos(t2), L2 * np.sin(t2)); f = (k[0] + L3 * np.cos(t2 - t3), k[1] + L3 * np.sin(t2 - t3))
            (ax_, ay_), (bx, by), (fx, fy) = side(0, 0), side(*k), side(*f)
            out.append(f"<line x1='{ax_}' y1='{ay_}' x2='{bx}' y2='{by}' stroke='#2a6fb0' stroke-width='8' stroke-linecap='round'/>"
                       f"<line x1='{bx}' y1='{by}' x2='{fx}' y2='{fy}' stroke='currentColor' stroke-width='6' stroke-linecap='round'/>")
            ex, ey = top(L1 * np.cos(t1), L1 * np.sin(t1)); qx, qy = top((L1 + k[0] + L3 * np.cos(t2 - t3)) * np.cos(t1), (L1 + k[0] + L3 * np.cos(t2 - t3)) * np.sin(t1))
            out.append(f"<line x1='{ox}' y1='{oy}' x2='{ex}' y2='{ey}' stroke='currentColor' stroke-width='6' stroke-linecap='round'/>"
                       f"<line x1='{ex}' y1='{ey}' x2='{qx}' y2='{qy}' stroke='#2a6fb0' stroke-width='5' stroke-linecap='round'/>")
        out.append("</svg>")
        return "".join(out)

    if not ok4:
        _out = mo.callout(mo.md(t("play_wait")), kind="neutral")
    else:
        try:
            _ang = ik(sx.value, sy.value, sz.value)
        except Exception as e:
            _ang = None
        _txt = (t("play_none") if _ang is None else
                f"θ1 = **{_ang[0]:.1f}°**, θ2 = **{_ang[1]:.1f}°**, θ3 = **{_ang[2]:.1f}°**")
        _out = mo.vstack([mo.Html(_svg(sx.value, sy.value, sz.value, _ang)), mo.md(_txt)])
    _out
    return


@app.cell(hide_code=True)
def _(mo, t):
    shape = mo.ui.dropdown(options={t("sq"): "square", t("circle"): "circle", t("star"): "star"}, value=t("sq"), label=t("shape"))
    size = mo.ui.slider(20, 80, value=40, step=5, label=t("size"), show_value=True)
    mo.vstack([mo.md(t("r1_md")), mo.hstack([shape, size], justify="start")])
    return shape, size


@app.cell(hide_code=True)
def _(fk, ik, mo, np, ok5, player, shape, size, t):
    def _path(kind, a, n=300):
        c = np.array([162.0, 0.0, -89.5])
        s = np.linspace(0, 1, n, endpoint=False)
        if kind == "circle":
            pts = [c + [a / 2 * np.cos(2 * np.pi * v), a / 2 * np.sin(2 * np.pi * v), 0] for v in s]
        else:
            if kind == "square":
                corners = np.array([[-1, -1], [1, -1], [1, 1], [-1, 1]]) * a / 2
            else:
                k = np.arange(5) * 4 * np.pi / 5 + np.pi / 2
                corners = np.c_[np.cos(k), np.sin(k)] * a / 2
            m = len(corners); pts = []
            for v in s:
                i = int(v * m); f = v * m - i
                p = corners[i] + f * (corners[(i + 1) % m] - corners[i])
                pts.append(c + [p[0], p[1], 0])
        return np.array(pts)

    if not ok5:
        _out = mo.callout(mo.md("🔒 " + t("r_locked")), kind="neutral")
    else:
        _P = _path(shape.value, size.value)
        _angles, _bad = [], 0
        for _p in _P:
            _a = ik(*_p)
            if _a is None:
                _bad += 1; _angles.append(None)
            else:
                _angles.append([round(float(v), 3) for v in _a])
        _err = max((np.linalg.norm(fk(*a) - p) for a, p in zip(_angles, _P) if a is not None), default=0)
        _cfg = {"mode": "leg", "angles": [[a] if a else [None] for a in _angles],
                "target": _P.round(2).tolist(), "fps": 60}
        _msg = t("r1_done").format(n=len(_P), err=_err) + ("" if not _bad else " " + t("r1_bad").format(b=_bad))
        _out = mo.vstack([player(_cfg, 360), mo.callout(mo.md("🎉 " + _msg), kind="success")])
    _out
    return


@app.cell(hide_code=True)
def _(mo, t):
    mo.md(t("r2_md"))
    return


@app.cell(hide_code=True)
def _(np):
    # Body "dance": same motion as the website hero. Feet stay planted on the ground.
    MOUNTS = [(85.2, -49.2, -30), (0, -98.4, -90), (-85.2, -49.2, -150),
              (85.2, 49.2, 30), (0, 98.4, 90), (-85.2, 49.2, 150)]   # R1 R2 R3 L1 L2 L3: x, y, alpha
    FEET = np.array([[mx + 162 * np.cos(np.radians(a)), my + 162 * np.sin(np.radians(a)), -89.5] for mx, my, a in MOUNTS])

    def rot(roll, pitch, yaw):
        r, p, y = np.radians([roll, pitch, yaw])
        Rx = np.array([[1, 0, 0], [0, np.cos(r), -np.sin(r)], [0, np.sin(r), np.cos(r)]])
        Ry = np.array([[np.cos(p), 0, np.sin(p)], [0, 1, 0], [-np.sin(p), 0, np.cos(p)]])
        Rz = np.array([[np.cos(y), -np.sin(y), 0], [np.sin(y), np.cos(y), 0], [0, 0, 1]])
        return Rz @ Ry @ Rx

    def dance(t, T_total=12.0):
        w = 2 * np.pi / 6
        pose = np.array([20 * np.sin(w * t), 18 * np.sin(2 * w * t), 12 * np.sin(1.5 * w * t),
                         5 * np.sin(w * t + 1), 5 * np.sin(2 * w * t), 8 * np.sin(w * t)])
        ramp = min(1.0, t / 1.5, (T_total - t) / 1.5)       # ease in/out so it starts & ends at home
        ramp = max(0.0, ramp) ** 2 * (3 - 2 * max(0.0, ramp))
        return pose * ramp

    def foot_in_leg_frame(i, pose):
        """World foot i -> target in leg i's own frame (this is Stage 5 material; given for now)."""
        R = rot(*pose[3:])
        pb = R.T @ (FEET[i] - pose[:3])
        mx, my, a = MOUNTS[i]
        ca, sa = np.cos(np.radians(a)), np.sin(np.radians(a))
        dx, dy = pb[0] - mx, pb[1] - my
        return np.array([ca * dx + sa * dy, -sa * dx + ca * dy, pb[2]])
    return FEET, MOUNTS, dance, foot_in_leg_frame, rot


@app.cell(hide_code=True)
def _(FEET, MOUNTS, dance, fk, foot_in_leg_frame, ik, mo, np, ok5, player, rot, t):
    def _make():
        _fps, _T = 50, 12.0
        _frames, _poses, _slip, _bad = [], [], 0.0, 0
        for _k in range(int(_T * _fps) + 1):
            _pose = dance(_k / _fps, _T)
            _R = rot(*_pose[3:])
            _row = []
            for _i in range(6):
                _a = ik(*foot_in_leg_frame(_i, _pose))
                if _a is None:
                    _bad += 1; _row.append(None); continue
                _row.append([round(float(v), 3) for v in _a])
                # where does the foot REALLY go with your angles?
                _pl = fk(*_a); _mx, _my, _al = MOUNTS[_i]
                _c, _s = np.cos(np.radians(_al)), np.sin(np.radians(_al))
                _pb = np.array([_mx + _c * _pl[0] - _s * _pl[1], _my + _s * _pl[0] + _c * _pl[1], _pl[2]])
                _slip = max(_slip, float(np.linalg.norm(_R @ _pb + _pose[:3] - FEET[_i])))
            _frames.append(_row); _poses.append([round(float(v), 3) for v in _pose])
        return _frames, _poses, _slip, _bad

    if not ok5:
        dance_angles = None
        _out = mo.callout(mo.md("🔒 " + t("r_locked")), kind="neutral")
    else:
        _frames, _poses, _slip, _bad = _make()
        dance_angles = _frames
        _cfg = {"mode": "hex", "angles": _frames, "poses": _poses, "fps": 50}
        _ok = _slip < 0.5 and _bad == 0
        _msg = t("r2_done").format(slip=_slip) if _ok else t("r2_bad").format(slip=_slip, bad=_bad)
        _out = mo.vstack([player(_cfg, 420), mo.callout(mo.md(("🏆 " if _ok else "⚠️ ") + _msg), kind="success" if _ok else "warn")])
    _out
    return (dance_angles,)


@app.cell(hide_code=True)
def _(IN_BROWSER, mo, t):
    robot_on = mo.ui.switch(label=t("robot_switch"))
    send = mo.ui.run_button(label=t("robot_send"))
    mo.vstack([mo.md(t("robot_md")),
               mo.callout(mo.md(t("robot_browser")), kind="neutral") if IN_BROWSER else mo.hstack([robot_on, send], justify="start")])
    return robot_on, send


@app.cell(hide_code=True)
def _(IN_BROWSER, dance_angles, mo, np, robot_on, send, t):
    mo.stop(IN_BROWSER or not send.value)
    mo.stop(not robot_on.value, mo.callout(mo.md(t("robot_need_switch")), kind="warn"))
    mo.stop(dance_angles is None or any(a is None for row in dance_angles for a in row),
            mo.callout(mo.md(t("robot_need_dance")), kind="danger"))

    _thetas = np.array([np.concatenate(row) for row in dance_angles])          # (N, 18): R1..L3 × coxa/femur/tibia
    _peak = float(np.max(np.abs(np.diff(_thetas, axis=0))) * 50)               # deg/s at 50 Hz
    mo.stop(_peak > 100, mo.callout(mo.md(t("robot_fast").format(p=_peak)), kind="danger"))

    import pathlib, sys as _sys
    _code_dir = pathlib.Path(mo.notebook_dir()).resolve().parents[1]           # .../code
    if str(_code_dir) not in _sys.path:
        _sys.path.insert(0, str(_code_dir))
    from utils.link import Link

    _home = np.array([0, 30, 105] * 6, dtype=float)
    _link = Link()
    try:
        _link.move_to(_home, 2)
        _link.play(_thetas)
        _link.move_to(_home, 1.5)
    finally:
        _link.close()
    mo.callout(mo.md(t("robot_done").format(n=len(_thetas), p=_peak)), kind="success")
    return


@app.cell(hide_code=True)
def _(mo, t):
    mo.md(t("outro"))
    return


@app.cell(hide_code=True)
def _(mo, np, t):
    def check(fn, cases, tol=0.01, radians_hint=False):
        """Run fn on each case, compare to expected (None means 'should return None')."""
        rows, passed, rad = [], 0, False
        for args, exp in cases:
            try:
                got = fn(*args)
            except Exception as e:
                got = f"error: {type(e).__name__}: {e}"
            ok = False
            if isinstance(got, str):
                shown = got
            elif exp is None:
                ok, shown = got is None, "None" if got is None else str(np.round(np.asarray(got, dtype=float), 3).tolist())
            elif got is None:
                shown = "None"
            else:
                g, e = np.atleast_1d(np.asarray(got, dtype=float)), np.atleast_1d(np.asarray(exp, dtype=float))
                ok = g.shape == e.shape and bool(np.all(np.abs(g - e) <= tol))
                if radians_hint and g.shape == e.shape and np.all(np.abs(np.degrees(g) - e) <= tol) and np.any(np.abs(e) > tol):
                    rad = True
                shown = str(np.round(g, 3).tolist()) if g.size > 1 else f"{g[0]:.3f}"
            passed += ok
            exp_s = "None" if exp is None else (str(list(exp)) if isinstance(exp, tuple) else f"{exp:.3f}")
            rows.append((", ".join(str(a) for a in args), exp_s, shown, "✓" if ok else "✗"))
        all_ok = passed == len(cases)
        table = t("th") + "\n|---|---|---|---|\n" + "\n".join(f"| `{a}` | `{e}` | `{g}` | {m} |" for a, e, g, m in rows)
        if all_ok:
            head = "✅ " + t("pass").format(n=len(cases))
        elif all(r[2] == "None" for r in rows):
            head = "✏️ " + t("not_started")
        else:
            head = "❌ " + t("fail").format(p=passed, n=len(cases))
            if rad:
                head += "  \n💡 " + t("rad_hint")
        return all_ok, mo.callout(mo.md(head + "\n\n" + table), kind="success" if all_ok else ("neutral" if head.startswith("✏️") else "danger"))
    return (check,)


@app.cell(hide_code=True)
def _(json, mo):
    HEXVIEW_JS = r"""/* HexView: tiny 3D-ish renderer for the Macaroon hexapod (shared by site + notebook). */
const HX = (() => {
  const L1 = 62, L2 = 76, L3 = 132, D2R = Math.PI / 180;
  const LEGS = [ // R1 R2 R3 L1 L2 L3 : mount (mm), alpha (deg)
    { n: 'R1', m: [85.2, -49.2], a: -30 }, { n: 'R2', m: [0, -98.4], a: -90 }, { n: 'R3', m: [-85.2, -49.2], a: -150 },
    { n: 'L1', m: [85.2, 49.2], a: 30 }, { n: 'L2', m: [0, 98.4], a: 90 }, { n: 'L3', m: [-85.2, 49.2], a: 150 }];
  const COLORS = ['#e65546', '#f09632', '#cdaa28', '#3c82dc', '#3cafaa', '#8264d2'];
  // reference ik in leg frame (knee-up), returns [t1,t2,t3] deg or null
  function ik(x, y, z) {
    const t1 = Math.atan2(y, x) / D2R, u = Math.hypot(x, y) - L1, D = Math.hypot(u, z);
    const c = (D * D - L2 * L2 - L3 * L3) / (2 * L2 * L3);
    if (Math.abs(c) > 1) return null;
    const t3 = Math.acos(c);
    const t2 = Math.atan2(z, u) + Math.atan2(L3 * Math.sin(t3), L2 + L3 * Math.cos(t3));
    const r = [t1, t2 / D2R, t3 / D2R];
    if (Math.abs(r[0]) > 45 || Math.abs(r[1]) > 75 || r[2] < 15 || r[2] > 165) return null;
    return r;
  }
  // leg-frame points for angles
  function legPts(t) {
    const c1 = Math.cos(t[0] * D2R), s1 = Math.sin(t[0] * D2R), t2 = t[1] * D2R, t23 = (t[1] - t[2]) * D2R;
    const rk = L1 + L2 * Math.cos(t2), zk = L2 * Math.sin(t2), rt = rk + L3 * Math.cos(t23), zt = zk + L3 * Math.sin(t23);
    return [[0, 0, 0], [L1 * c1, L1 * s1, 0], [rk * c1, rk * s1, zk], [rt * c1, rt * s1, zt]];
  }
  function rot(rpy) { // R = Rz(yaw) Ry(pitch) Rx(roll)
    const [r, p, y] = rpy.map(v => v * D2R), cr = Math.cos(r), sr = Math.sin(r), cp = Math.cos(p), sp = Math.sin(p), cy = Math.cos(y), sy = Math.sin(y);
    return [[cy * cp, cy * sp * sr - sy * cr, cy * sp * cr + sy * sr], [sy * cp, sy * sp * sr + cy * cr, sy * sp * cr - cy * sr], [-sp, cp * sr, cp * cr]];
  }
  const mul = (R, v) => [R[0][0] * v[0] + R[0][1] * v[1] + R[0][2] * v[2], R[1][0] * v[0] + R[1][1] * v[1] + R[1][2] * v[2], R[2][0] * v[0] + R[2][1] * v[1] + R[2][2] * v[2]];
  const mulT = (R, v) => [R[0][0] * v[0] + R[1][0] * v[1] + R[2][0] * v[2], R[0][1] * v[0] + R[1][1] * v[1] + R[2][1] * v[2], R[0][2] * v[0] + R[1][2] * v[1] + R[2][2] * v[2]];
  // body -> world for pose [x,y,z,roll,pitch,yaw]
  function legWorld(leg, t, pose) {
    const R = rot(pose.slice(3)), ca = Math.cos(leg.a * D2R), sa = Math.sin(leg.a * D2R);
    return legPts(t).map(p => { const b = [leg.m[0] + ca * p[0] - sa * p[1], leg.m[1] + sa * p[0] + ca * p[1], p[2]]; const w = mul(R, b); return [w[0] + pose[0], w[1] + pose[1], w[2] + pose[2]]; });
  }
  const HOME_H = 89.5;
  const FEET = LEGS.map(l => { const ca = Math.cos(l.a * D2R), sa = Math.sin(l.a * D2R); return [l.m[0] + 162 * ca, l.m[1] + 162 * sa, -HOME_H]; });
  function danceT(t) { // body pose at time t (s), same as notebook's dance()
    const w = 2 * Math.PI / 6;
    return [20 * Math.sin(w * t), 18 * Math.sin(2 * w * t), 12 * Math.sin(1.5 * w * t), 5 * Math.sin(w * t + 1), 5 * Math.sin(2 * w * t), 8 * Math.sin(w * t)];
  }
  function bodyIK(pose) { // world feet -> leg-frame targets -> ik
    const R = rot(pose.slice(3));
    return LEGS.map((l, i) => {
      const pb = mulT(R, [FEET[i][0] - pose[0], FEET[i][1] - pose[1], FEET[i][2] - pose[2]]);
      const dx = pb[0] - l.m[0], dy = pb[1] - l.m[1], ca = Math.cos(l.a * D2R), sa = Math.sin(l.a * D2R);
      return ik(ca * dx + sa * dy, -sa * dx + ca * dy, pb[2]);
    });
  }
  // draw one frame. opts: {legs: indices, pose, angles:[[t1,t2,t3]|null...], trails, az, el, scale, body}
  function draw(ctx, W, H, o, col) {
    const az = o.az, el = o.el, s = o.scale, cx = W / 2 + (o.ox || 0), cy = H * (o.cy || 0.62);
    const P = p => { const xr = p[0] * Math.cos(az) - p[1] * Math.sin(az), yr = p[0] * Math.sin(az) + p[1] * Math.cos(az); return [cx + s * xr, cy - s * ((p[2] + (o.ground || HOME_H)) * Math.cos(el) + yr * Math.sin(el))]; };
    ctx.clearRect(0, 0, W, H);
    // ground grid
    ctx.strokeStyle = col.grid; ctx.lineWidth = 1;
    const g = o.gridR || 360;
    for (let k = -g; k <= g; k += 40) { let a = P([k, -g, -(o.ground || HOME_H)]), b = P([k, g, -(o.ground || HOME_H)]); ctx.beginPath(); ctx.moveTo(a[0], a[1]); ctx.lineTo(b[0], b[1]); ctx.stroke(); a = P([-g, k, -(o.ground || HOME_H)]); b = P([g, k, -(o.ground || HOME_H)]); ctx.beginPath(); ctx.moveTo(a[0], a[1]); ctx.lineTo(b[0], b[1]); ctx.stroke(); }
    // trails
    (o.trails || []).forEach((tr, i) => { if (!tr || tr.length < 2) return; ctx.strokeStyle = o.trailColor || col.accent; ctx.lineWidth = 2.5; ctx.beginPath(); tr.forEach((p, j) => { const q = P(p); j ? ctx.lineTo(q[0], q[1]) : ctx.moveTo(q[0], q[1]); }); ctx.stroke(); });
    (o.targets || []).forEach(tr => { if (!tr || tr.length < 2) return; ctx.strokeStyle = col.muted; ctx.setLineDash([4, 4]); ctx.lineWidth = 1.2; ctx.beginPath(); tr.forEach((p, j) => { const q = P(p); j ? ctx.lineTo(q[0], q[1]) : ctx.moveTo(q[0], q[1]); }); ctx.stroke(); ctx.setLineDash([]); });
    const legs = o.legDefs || o.legs.map(i => LEGS[i]);
    const pts = legs.map((l, k) => o.angles[k] ? legWorld(l, o.angles[k], o.pose) : null);
    // body
    if (o.body) {
      const R = rot(o.pose.slice(3)), order = [0, 1, 2, 5, 4, 3];
      ctx.fillStyle = col.body; ctx.strokeStyle = col.ink; ctx.lineWidth = 1.5; ctx.beginPath();
      order.forEach((i, j) => { const b = mul(R, [LEGS[i].m[0], LEGS[i].m[1], 0]); const q = P([b[0] + o.pose[0], b[1] + o.pose[1], b[2] + o.pose[2]]); j ? ctx.lineTo(q[0], q[1]) : ctx.moveTo(q[0], q[1]); });
      ctx.closePath(); ctx.fill(); ctx.stroke();
      const nose = mul(R, [70, 0, 0]), q0 = P([o.pose[0], o.pose[1], o.pose[2]]), q1 = P([nose[0] + o.pose[0], nose[1] + o.pose[1], nose[2] + o.pose[2]]);
      ctx.strokeStyle = col.ink; ctx.lineWidth = 2; ctx.beginPath(); ctx.moveTo(q0[0], q0[1]); ctx.lineTo(q1[0], q1[1]); ctx.stroke();
    }
    pts.forEach((p, k) => {
      if (!p) return; const c = o.legColor ? o.legColor : COLORS[o.legs ? o.legs[k] : 0];
      const sh = P([p[3][0], p[3][1], -(o.ground || HOME_H)]); ctx.fillStyle = col.grid; ctx.beginPath(); ctx.ellipse(sh[0], sh[1], 7, 3, 0, 0, 7); ctx.fill();
      ctx.strokeStyle = c; ctx.lineCap = 'round'; ctx.lineJoin = 'round';
      [[0, 1, 5], [1, 2, 7], [2, 3, 5]].forEach(([a, b, w]) => { const qa = P(p[a]), qb = P(p[b]); ctx.lineWidth = w; ctx.beginPath(); ctx.moveTo(qa[0], qa[1]); ctx.lineTo(qb[0], qb[1]); ctx.stroke(); });
      ctx.fillStyle = col.ink; p.slice(0, 3).forEach(pp => { const q = P(pp); ctx.beginPath(); ctx.arc(q[0], q[1], 3.5, 0, 7); ctx.fill(); });
      const qt = P(p[3]); ctx.fillStyle = c; ctx.beginPath(); ctx.arc(qt[0], qt[1], 4.5, 0, 7); ctx.fill();
    });
    return pts;
  }
  return { L1, L2, L3, LEGS, COLORS, FEET, ik, legPts, legWorld, rot, danceT, bodyIK, draw, HOME_H };
})();
"""

    def player(cfg, height=400):
        """Animate leg / hexapod from YOUR joint angles (the JS only does forward kinematics)."""
        html = """<!doctype html><html><head><meta charset='utf-8'><style>
        :root{--ink:#16202a;--muted:#5b6875;--grid:#e4e9ee;--accent:#d9771f;--body:#e9edf1;--bg:#fff}
        @media (prefers-color-scheme: dark){:root{--ink:#e3e9ef;--muted:#98a5b2;--grid:#26313c;--accent:#f0954a;--body:#26323e;--bg:#17202a}}
        html,body{margin:0;background:var(--bg);font:12px monospace;color:var(--muted)}
        canvas{width:100%;height:calc(100vh - 6px);display:block;cursor:grab;touch-action:none}
        #lbl{position:absolute;left:10px;top:8px}</style></head><body><div id='lbl'></div><canvas id='c'></canvas><script>"""
        html += HEXVIEW_JS
        html += "\nconst CFG=" + json.dumps(cfg) + ";\n"
        html += r"""
        const cv=document.getElementById('c'),ctx=cv.getContext('2d');
        const css=n=>getComputedStyle(document.documentElement).getPropertyValue(n).trim();
        const C={ink:css('--ink'),muted:css('--muted'),grid:css('--grid'),accent:css('--accent'),body:css('--body')};
        function fit(){const r=cv.getBoundingClientRect();cv.width=r.width*devicePixelRatio;cv.height=r.height*devicePixelRatio;}
        fit();addEventListener('resize',fit);
        let az=CFG.mode==='leg'?-0.55:-0.75,lx=null;
        cv.onpointerdown=e=>{lx=e.clientX;cv.setPointerCapture(e.pointerId)};cv.onpointermove=e=>{if(lx!=null){az+=(e.clientX-lx)*0.01;lx=e.clientX}};cv.onpointerup=()=>lx=null;
        const N=CFG.angles.length,trail=[];let t0=performance.now();
        const LEG=[{m:[0,0],a:0}];
        function frame(now){
          const k=Math.max(0,Math.floor((now-t0)/1000*CFG.fps))%N;
          if(k===0&&trail.length>N/2)trail.length=0;
          const s=Math.min(cv.width,cv.height*1.35)/(CFG.mode==='leg'?230:620);
          if(CFG.mode==='leg'){
            const pts=HX.draw(ctx,cv.width,cv.height,{legDefs:LEG,angles:CFG.angles[k],pose:[0,0,0,0,0,0],az,el:0.55,scale:s,body:false,ox:-s*95,cy:0.78,gridR:200,
              trails:[trail],targets:[CFG.target.concat([CFG.target[0]])]},C);
            if(pts[0])trail.push(pts[0][3]);
            document.getElementById('lbl').textContent='frame '+k+'/'+N+(CFG.angles[k][0]?'':'  ✗ ik() returned None');
          }else{
            HX.draw(ctx,cv.width,cv.height,{legs:[0,1,2,3,4,5],angles:CFG.angles[k],pose:CFG.poses[k],az,el:0.5,scale:s,body:true,cy:0.62},C);
            document.getElementById('lbl').textContent='t = '+(k/CFG.fps).toFixed(2)+' s';
          }
          requestAnimationFrame(frame);
        }
        requestAnimationFrame(frame);
        </script></body></html>"""
        return mo.iframe(html, height=f"{height}px")
    return (player,)


@app.cell(hide_code=True)
def _():
    TEXT = {
        "en": {
            "crumb": "Stage 3 · Inverse Kinematics · practice",
            "intro": """# Make the leg go where you point 🦿
    
    You'll build `ik(x, y, z)` in **4 small pieces**. After each piece, a checker runs instantly and tells you exactly which test passed or failed.
    Finish all of them to unlock two rewards: **one leg drawing shapes**, then **the whole hexapod dancing**, both driven by *your* code.
    
    How to work: edit the code cells marked ✏️, then run them (Ctrl/Cmd + Enter). The checker below each one updates on its own. If you're stuck, open the hints one at a time; the last one is the full answer.""",
            "roundtrip": "round trip",
            "all_unlocked": "All checkpoints passed. Rewards unlocked below!",
            "locked_n": "{n} checkpoint(s) left before the rewards unlock.",
            "given_md": """## What you're given
    
    These come from Stage 1. The leg frame: **x** points straight out from the body, **y** to the left, **z** up. Angles are in degrees.
    
    - **θ1** (coxa): left/right swing, 0° = straight out.
    - **θ2** (femur): up/down, measured from horizontal, up is positive.
    - **θ3** (tibia/knee): how much the tibia bends away from the femur's direction. 0° = straight, 90° = right angle.
    
    The standing pose is (0°, 30°, 105°), which puts the foot at about **(162, 0, −89.5)**. Run the cell to see it.""",
            "hint": "Hint",
            "answer": "Answer (try the hints first!)",
            "ex1_md": """## ✏️ 1 · Turn to face the target
    
    From above, the coxa just has to point the leg at (x, y). Write `solve_theta1(x, y)` that returns that direction **in degrees**.""",
            "ex1_h1": "It's the angle of the point (x, y) measured from the +x axis. Which numpy function takes y and x separately so it knows the quadrant?",
            "ex1_h2": "`np.arctan2(y, x)` gives radians. `np.degrees(...)` converts.",
            "ex1_a": "```python\nreturn np.degrees(np.arctan2(y, x))\n```",
            "ex2_md": """## ✏️ 2 · Flatten to 2D
    
    After turning, everything happens in one vertical plane. Return `(u, z)`: **u** is how far the target is horizontally from the **femur joint** (not the coxa!), and z is unchanged.
    
    Picture: the femur joint sits L1 = 62 mm out along the coxa link.""",
            "ex2_h1": "First the horizontal distance from the coxa: r = √(x² + y²). Then subtract the coxa link length L1.",
            "ex2_a": "```python\nr = np.hypot(x, y)\nreturn r - L1, z\n```",
            "ex3_md": """## ✏️ 3 · Solve the triangle for the knee
    
    Femur (L2 = 76), tibia (L3 = 132) and the line D from femur joint to the target form a triangle. Use the law of cosines to get **θ3 in degrees**.
    
    If the target is out of reach (D > 208 or D < 56), `arccos` has no answer, so return **None**.""",
            "ex3_h1": "D = √(u² + z²). Law of cosines in our convention: cos θ3 = (D² − L2² − L3²) / (2·L2·L3).",
            "ex3_h2": "Compute c first. If c > 1 or c < −1, return None. Otherwise θ3 = arccos(c), converted to degrees.",
            "ex3_a": "```python\nD = np.hypot(u, z)\nc = (D**2 - L2**2 - L3**2) / (2 * L2 * L3)\nif abs(c) > 1:\n    return None\nreturn np.degrees(np.arccos(c))\n```",
            "ex4_md": """## ✏️ 4 · The femur angle
    
    θ2 = **α + β**. α is the direction from the femur joint to the target. β is the triangle's corner at the femur joint (between the D line and the femur).
    
    Careful: α + β can come out above 180°. Wrap the answer back into [−180°, 180°] (one test checks this; it's a real bug we hit!).""",
            "ex4_h1": "α = atan2(z, u). For β, imagine the femur lying flat on the x-axis: the foot would be at (L2 + L3·cos θ3, L3·sin θ3). β is the atan2 of that point.",
            "ex4_h2": "Remember θ3 comes in as degrees, but np.sin / np.cos want radians. To wrap: `(v + 180) % 360 - 180`.",
            "ex4_a": "```python\nt3 = np.radians(theta3)\nalpha = np.arctan2(z, u)\nbeta = np.arctan2(L3 * np.sin(t3), L2 + L3 * np.cos(t3))\nv = np.degrees(alpha + beta)\nreturn (v + 180) % 360 - 180\n```",
            "ex5_md": """## 5 · Put it together, then prove it
    
    `ik()` below just chains your four pieces and refuses angles outside the servo limits. Read it; you don't need to change it.
    
    Then the **round-trip test**: pick 500 random legal joint angles, compute the foot with `fk`, ask your `ik` to find angles for that foot, run `fk` again. If your IK is right, you land on the same point every time. This is the standard way robotics engineers test IK.""",
            "rt_wait": "Finish checkpoints 1–4 first, then the round-trip test runs here.",
            "rt_score": "**{good}/{n}** random targets came back to the same point. Worst error: {worst:.2e} mm.",
            "rt_far": "- ✗ A target that is out of reach (or outside the coxa limit) did not return None.",
            "rt_pass": "**Round trip passed. Your IK is correct.** Scroll down for your rewards.",
            "play_md": "## 🎮 Playground\nMove the target with the sliders. The orange circle is the target; the leg is drawn from **your** ik() angles.",
            "play_wait": "Unlocks after checkpoint 4.",
            "play_none": "ik() returned **None**: out of reach or past a joint limit. Try the z slider.",
            "sq": "square", "circle": "circle", "star": "star", "shape": "shape", "size": "size (mm)",
            "r1_md": "## ★ Reward 1 · Draw with the leg\nYour ik() turns every point of the path into three angles. The animation only does **forward** kinematics on your angles, so if your IK were wrong, the orange trail would miss the dashed path. Drag to rotate.",
            "r_locked": "Locked. Pass the round-trip test to unlock.",
            "r1_done": "Your ik() solved {n} points. Biggest gap between the path and where the foot really went: {err:.1e} mm.",
            "r1_bad": "{b} points were out of reach (try a smaller size).",
            "r2_md": "## ★★ Reward 2 · Make the whole robot dance\nNow all six legs. The body sways, rolls and turns, while each foot should stay **planted** on the ground. Each frame we work out where every foot is relative to its own leg, and your `ik()` does the rest: 6 legs × 601 frames ≈ 3,600 IK solves.",
            "r2_done": "**Your code is driving a hexapod.** 3,606 IK solves, and the feet slipped at most {slip:.1e} mm. That's what you'd send to the real robot.",
            "r2_bad": "Feet slipped up to {slip:.1f} mm and {bad} solves failed. Something in ik() isn't quite right yet.",
            "robot_md": "## 🤖 Bonus · Run it on the real robot\nSame dance, sent through `utils/link.py` at 50 Hz. Before sending, the notebook checks that every frame solved and that no joint goes faster than 100°/s. The robot first moves to home, dances for 12 s, then returns home. **Hold the robot up or put it on the floor with space around it; keep the USB cable slack.**",
            "robot_browser": "This part only works when you run the notebook locally (`marimo edit ...`) with the robot plugged in. The browser can't open your serial port.",
            "robot_switch": "Robot is connected and powered",
            "robot_send": "▶ Send the dance",
            "robot_need_switch": "Turn on the switch first to confirm the robot is ready.",
            "robot_need_dance": "Finish Reward 2 with no failed solves first.",
            "robot_fast": "Peak joint speed would be {p:.0f}°/s (> 100°/s). Not sending.",
            "robot_done": "Done: sent {n} frames, peak joint speed {p:.0f}°/s. 🎉",
            "th": "| input | expected | yours | |",
            "pass": "All {n} tests passed.",
            "fail": "{p}/{n} tests passed.",
            "not_started": "Not started yet: write your code in the cell above and run it.",
            "rad_hint": "Your numbers look like **radians**. Convert with `np.degrees(...)`.",
            "outro": """## What you just learned
    - **IK = undo FK**, by splitting it up: turn (top view) → flatten (u, z) → triangle (law of cosines) → aim + lift (α + β).
    - Some targets have **no** solution (outside the 56–208 mm ring), some have **two** (knee up/down), and real servos rule some out.
    - **Always test IK with a round trip** through FK.
    
    **Going further (optional):** with the femur raised and the knee folded tight, the foot can end up *behind* the coxa joint (x < 0). Your `ik()` returns None there, and the round-trip test skips those poses. Can you handle them? (Hint: turn the coxa the other way and let r be negative.)
    
    **Next: Stage 4 · Jacobian.** If the foot moves 1 mm, how much do the joints move, and how hard do the servos have to push?""",
        },
        "zh": {
            "crumb": "阶段 3 · 逆运动学 · 练习",
            "intro": """# 指哪，腿就去哪 🦿
    
    你会分 **4 小块**拼出 `ik(x, y, z)`。每写完一块，下面的检查器立刻运行，告诉你哪个测试过了、哪个没过。
    全部完成后解锁两个奖励：**一条腿画图形**，然后**整只六足机器人跳舞**，都由*你写的代码*驱动。
    
    怎么做：修改标了 ✏️ 的代码格子，然后运行（Ctrl/Cmd + Enter），下面的检查器会自动更新。卡住了就一条一条展开提示，最后一条是完整答案。""",
            "roundtrip": "回环测试",
            "all_unlocked": "全部检查点通过，奖励已在下方解锁！",
            "locked_n": "还差 {n} 个检查点解锁奖励。",
            "given_md": """## 已经给你的东西
    
    这些来自阶段 1。腿坐标系：**x** 从机身指向腿的正前方，**y** 向左，**z** 向上。角度单位是度。
    
    - **θ1**（coxa）：左右摆，0° = 正前方。
    - **θ2**（femur）：上下摆，从水平往上量，向上为正。
    - **θ3**（tibia / 膝）：tibia 相对 femur 方向弯过去多少。0° = 伸直，90° = 直角。
    
    站立姿态是 (0°, 30°, 105°)，脚尖大约在 **(162, 0, −89.5)**。运行这个格子看看。""",
            "hint": "提示",
            "answer": "答案（先试试提示！）",
            "ex1_md": """## ✏️ 1 · 转身对准目标
    
    从上往下看，coxa 只需要让腿指向 (x, y)。写 `solve_theta1(x, y)`，返回这个方向，**单位是度**。""",
            "ex1_h1": "就是点 (x, y) 从 +x 轴量起的角度。哪个 numpy 函数分别接收 y 和 x，从而能判断象限？",
            "ex1_h2": "`np.arctan2(y, x)` 返回弧度，用 `np.degrees(...)` 换成度。",
            "ex1_a": "```python\nreturn np.degrees(np.arctan2(y, x))\n```",
            "ex2_md": """## ✏️ 2 · 压平成 2D
    
    转好以后，所有事情都在一个竖直平面里发生。返回 `(u, z)`：**u** 是目标离 **femur 关节**（不是 coxa！）的水平距离，z 不变。
    
    想象一下：femur 关节在 coxa 连杆往外 L1 = 62 mm 的地方。""",
            "ex2_h1": "先求离 coxa 的水平距离 r = √(x² + y²)，再减去 coxa 连杆长度 L1。",
            "ex2_a": "```python\nr = np.hypot(x, y)\nreturn r - L1, z\n```",
            "ex3_md": """## ✏️ 3 · 解三角形求膝盖角
    
    femur（L2 = 76）、tibia（L3 = 132），以及从 femur 关节到目标的直线 D，围成一个三角形。用余弦定理求 **θ3（度）**。
    
    如果目标够不着（D > 208 或 D < 56），`arccos` 无解，返回 **None**。""",
            "ex3_h1": "D = √(u² + z²)。按我们的约定，余弦定理写成：cos θ3 = (D² − L2² − L3²) / (2·L2·L3)。",
            "ex3_h2": "先算出 c。如果 c > 1 或 c < −1，返回 None；否则 θ3 = arccos(c)，再换成度。",
            "ex3_a": "```python\nD = np.hypot(u, z)\nc = (D**2 - L2**2 - L3**2) / (2 * L2 * L3)\nif abs(c) > 1:\n    return None\nreturn np.degrees(np.arccos(c))\n```",
            "ex4_md": """## ✏️ 4 · femur 角
    
    θ2 = **α + β**。α 是从 femur 关节指向目标的方向；β 是三角形在 femur 关节处的角（夹在 D 线和 femur 之间）。
    
    注意：α + β 可能超过 180°。要把结果绕回 [−180°, 180°]（有一个测试专门查这个，这是我们真踩过的坑！）。""",
            "ex4_h1": "α = atan2(z, u)。求 β 时，想象 femur 平放在 x 轴上：脚尖会在 (L2 + L3·cos θ3, L3·sin θ3)。β 就是这个点的 atan2。",
            "ex4_h2": "θ3 传进来是度，但 np.sin / np.cos 要的是弧度。绕回范围：`(v + 180) % 360 - 180`。",
            "ex4_a": "```python\nt3 = np.radians(theta3)\nalpha = np.arctan2(z, u)\nbeta = np.arctan2(L3 * np.sin(t3), L2 + L3 * np.cos(t3))\nv = np.degrees(alpha + beta)\nreturn (v + 180) % 360 - 180\n```",
            "ex5_md": """## 5 · 拼起来，然后证明它是对的
    
    下面的 `ik()` 只是把你的四块串起来，并拒绝超出舵机限位的角度。读一读就好，不用改。
    
    然后是**回环测试**：随机取 500 组合法关节角，用 `fk` 算出脚尖，让你的 `ik` 为这个脚尖求角度，再跑一次 `fk`。IK 正确的话，每次都会回到同一个点。这是机器人工程师测试 IK 的标准方法。""",
            "rt_wait": "先完成检查点 1–4，回环测试会在这里运行。",
            "rt_score": "**{good}/{n}** 个随机目标回到了原点。最大误差：{worst:.2e} mm。",
            "rt_far": "- ✗ 有一个够不着（或超出 coxa 限位）的目标没有返回 None。",
            "rt_pass": "**回环测试通过，你的 IK 是对的。** 往下翻领奖励。",
            "play_md": "## 🎮 试玩区\n用滑块移动目标。橙色圆圈是目标，腿是用**你的** ik() 算出的角度画的。",
            "play_wait": "完成检查点 4 后解锁。",
            "play_none": "ik() 返回了 **None**：够不着或超出关节限位。试试拖 z 滑块。",
            "sq": "正方形", "circle": "圆", "star": "五角星", "shape": "图形", "size": "大小 (mm)",
            "r1_md": "## ★ 奖励 1 · 用腿画画\n你的 ik() 把路径上的每个点变成三个角度。动画只对你的角度做**正**运动学，所以如果 IK 错了，橙色轨迹就会偏离虚线路径。拖动可以旋转。",
            "r_locked": "未解锁。通过回环测试后解锁。",
            "r1_done": "你的 ik() 解了 {n} 个点。路径和脚尖实际位置的最大偏差：{err:.1e} mm。",
            "r1_bad": "有 {b} 个点够不着（试试小一点的尺寸）。",
            "r2_md": "## ★★ 奖励 2 · 让整只机器人跳舞\n现在是六条腿。机身前后左右晃、侧倾、转头，而每只脚都应该**钉在地上不动**。每一帧我们算出每只脚相对它自己那条腿的位置，剩下的交给你的 `ik()`：6 条腿 × 601 帧 ≈ 3600 次 IK 求解。",
            "r2_done": "**你的代码正在驱动一只六足机器人。** 3606 次 IK 求解，脚最多滑动了 {slip:.1e} mm。这就是要发给实机的数据。",
            "r2_bad": "脚滑动了最多 {slip:.1f} mm，有 {bad} 次求解失败。ik() 里还有地方不太对。",
            "robot_md": "## 🤖 加分项 · 在实机上跑\n同一段舞，通过 `utils/link.py` 以 50 Hz 发送。发送前 notebook 会检查每一帧都解出来了，且没有关节超过 100°/s。机器人先回到 home，跳 12 秒，再回 home。**把机器人架空，或放在周围有空间的地上；USB 线留松一点。**",
            "robot_browser": "这一部分只有在本地运行 notebook（`marimo edit ...`）并插着机器人时才能用。浏览器打不开你的串口。",
            "robot_switch": "机器人已连接并上电",
            "robot_send": "▶ 发送这段舞",
            "robot_need_switch": "先打开开关，确认机器人准备好了。",
            "robot_need_dance": "先完成奖励 2，并且没有求解失败。",
            "robot_fast": "关节峰值速度会达到 {p:.0f}°/s（> 100°/s），不发送。",
            "robot_done": "完成：发送了 {n} 帧，关节峰值速度 {p:.0f}°/s。🎉",
            "th": "| 输入 | 期望 | 你的结果 | |",
            "pass": "{n} 个测试全部通过。",
            "fail": "通过 {p}/{n} 个测试。",
            "not_started": "还没开始：在上面的格子里写代码并运行。",
            "rad_hint": "你的结果看起来是**弧度**，用 `np.degrees(...)` 换成度。",
            "outro": """## 你刚刚学会了什么
    - **IK 就是把 FK 反过来**，靠拆分：转身（俯视）→ 压平 (u, z) → 三角形（余弦定理）→ 瞄准 + 抬起（α + β）。
    - 有的目标**无解**（在 56–208 mm 环外），有的有**两个解**（膝盖朝上/朝下），真实舵机还会排除一些解。
    - **测试 IK 一定要做回环**：再过一遍 FK。
    
    **挑战（选做）：**femur 抬高、膝盖折紧时，脚尖可能跑到 coxa 关节*后面*（x < 0）。你的 `ik()` 在那里会返回 None，回环测试也跳过了这些姿态。你能处理它们吗？（提示：coxa 往反方向转，让 r 取负。）
    
    **下一站：阶段 4 · Jacobian。** 脚尖移动 1 mm，关节要转多少？舵机要用多大的力？""",
        },
    }
    return (TEXT,)


if __name__ == "__main__":
    app.run()
