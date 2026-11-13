import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium", app_title="HexPod Academy · Stage 5 Body IK")


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
def _(mo, ok1, ok2, ok3, ok4, t):
    _steps = [ok1, ok2, ok3, ok4]
    _names = ["frames", "body_ik", "range", "plan"]
    _chips = " ".join(
        f"<span style='display:inline-block;padding:2px 10px;margin:2px;border-radius:99px;"
        f"background:{'#2b8a5733' if s else '#8882'};font-family:monospace;font-size:13px'>"
        f"{'✓' if s else '○'} {i + 1} · {n}</span>" for i, (s, n) in enumerate(zip(_steps, _names)))
    _done = sum(bool(s) for s in _steps)
    _reward = ("🏆 " + t("all_unlocked")) if _done == len(_steps) else ("🔒 " + t("locked_n").format(n=len(_steps) - _done))
    progress = mo.md(f"{_chips}<br><span style='font-size:14px'>{_reward}</span>")
    return (progress,)

@app.cell(hide_code=True)
def _(mo, t):
    mo.md(t("given_md"))
    return


@app.cell
def _(np):
    # ── Given (Stages 1 and 3) — you don't need to change anything here ──
    L1, L2, L3 = 62.0, 76.0, 132.0
    LIMITS = [(-45, 45), (-75, 75), (15, 165)]
    LEGS = ["R1", "R2", "R3", "L1", "L2", "L3"]
    MOUNTS = [(85.2, -49.2, -30), (0, -98.4, -90), (-85.2, -49.2, -150),     # (mx, my, alpha) per leg:
              (85.2, 49.2, 30), (0, 98.4, 90), (-85.2, 49.2, 150)]          # coxa position (mm), leg direction (deg)
    FEET = np.array([[mx + 162 * np.cos(np.radians(a)), my + 162 * np.sin(np.radians(a)), -89.5]
                     for mx, my, a in MOUNTS])                               # planted feet, world frame (mm)

    def fk(theta1, theta2, theta3):
        t1, t2, t23 = np.radians(theta1), np.radians(theta2), np.radians(theta2 - theta3)
        r = L1 + L2 * np.cos(t2) + L3 * np.cos(t23)
        return np.array([r * np.cos(t1), r * np.sin(t1), L2 * np.sin(t2) + L3 * np.sin(t23)])

    def ik(x, y, z):
        """Foot in the leg frame -> (θ1, θ2, θ3) in degrees, knee up; None if out of reach or past a limit."""
        t1 = np.degrees(np.arctan2(y, x))
        u = np.hypot(x, y) - L1
        c = (u * u + z * z - L2 * L2 - L3 * L3) / (2 * L2 * L3)
        if abs(c) > 1:
            return None
        t3 = np.arccos(c)
        t2 = np.degrees(np.arctan2(z, u) + np.arctan2(L3 * np.sin(t3), L2 + L3 * np.cos(t3)))
        a = np.array([t1, t2, np.degrees(t3)])
        if any(not lo - 1e-9 <= v <= hi + 1e-9 for v, (lo, hi) in zip(a, LIMITS)):
            return None
        return a
    return FEET, LEGS, MOUNTS, fk, ik


@app.cell(hide_code=True)
def _(mo, t):
    mo.vstack([mo.md(t("ex1_md")), mo.accordion({t("hint") + " 1": mo.md(t("ex1_h1")), t("hint") + " 2": mo.md(t("ex1_h2")), t("answer"): mo.md(t("ex1_a"))})])
    return


@app.cell
def _(MOUNTS, np):
    def rot(roll, pitch, yaw):
        """Body orientation (degrees) -> 3×3 rotation matrix R = Rz(yaw) · Ry(pitch) · Rx(roll)."""
        # ✏️ YOUR CODE HERE
        return None

    def to_leg_frame(f, pose, i):
        """World foot f, body pose (x, y, z, roll, pitch, yaw) -> the same foot in leg i's frame."""
        # ✏️ YOUR CODE HERE
        return None
    return rot, to_leg_frame


@app.cell(hide_code=True)
def _(FEET, check, mo, rot, to_leg_frame):
    _okR, _vR = check(lambda *a: None if rot(*a) is None else rot(*a).ravel(), [
        ((0, 0, 90), [0, -1, 0, 1, 0, 0, 0, 0, 1], "yaw 90° (flattened row by row)"),
        ((90, 0, 0), [1, 0, 0, 0, 0, -1, 0, 1, 0], "roll 90°"),
        ((0, 90, 0), [0, 0, 1, 0, 1, 0, -1, 0, 0], "pitch 90°"),
        ((10, 20, 30), [0.8138, -0.44097, 0.37852, 0.46985, 0.88256, 0.01803, -0.34202, 0.16318, 0.92542], "(10, 20, 30)")], tol=1e-4)
    _okL, _vL = check(to_leg_frame, [
        ((FEET[0], [0] * 6, 0), (162, 0, -89.5), "R1 foot, home pose"),
        ((FEET[4], [0] * 6, 4), (162, 0, -89.5), "L2 foot, home pose"),
        ((FEET[1], [20, 0, 0, 0, 0, 0], 1), (162, -20, -89.5), "R2 foot, body 20 mm forward"),
        ((FEET[0], [0, 0, 10, 0, 0, 10], 0), (158.0427, -45.2153, -99.5), "R1 foot, body up 10, yaw 10°"),
        ((FEET[3], [5, -10, 0, 8, -6, 12], 3), (141.6049, -52.594, -126.1913), "L1 foot, mixed pose")], tol=1e-3)
    ok1 = _okR and _okL
    mo.vstack([mo.md("`rot`"), _vR, mo.md("`to_leg_frame`"), _vL])
    return (ok1,)


@app.cell(hide_code=True)
def _(mo, t):
    mo.vstack([mo.md(t("ex2_md")), mo.accordion({t("hint") + " 1": mo.md(t("ex2_h1")), t("answer"): mo.md(t("ex2_a"))})])
    return


@app.cell
def _(FEET, LEGS, ik, np, to_leg_frame):
    def body_ik(pose):
        """Body pose -> (18 joint angles as one array, None), or (None, name of the first leg that can't reach)."""
        # ✏️ YOUR CODE HERE
        return None, None
    return (body_ik,)


@app.cell(hide_code=True)
def _(FEET, MOUNTS, body_ik, fk, mo, np, ok1, rot, t, verdict):
    def _world_feet(angles, pose):
        """Forward: joint angles + body pose -> where the six feet really are (world)."""
        R, out = rot(*pose[3:]), []
        for i, (mx, my, a) in enumerate(MOUNTS):
            p = fk(*angles[3 * i: 3 * i + 3])
            c, s = np.cos(np.radians(a)), np.sin(np.radians(a))
            pb = np.array([mx + c * p[0] - s * p[1], my + s * p[0] + c * p[1], p[2]])
            out.append(R @ pb + np.asarray(pose[:3], dtype=float))
        return np.array(out)

    def _run():
        if not ok1:
            return False, mo.callout(mo.md(t("ex2_wait")), kind="neutral")
        try:
            a0, leg0 = body_ik([0] * 6)
            a1, leg1 = body_ik([0, 0, 0, 30, 0, 0])
        except Exception as e:
            return False, verdict(False, [f"❌ error: {type(e).__name__}: {e}"])
        if a0 is None and leg0 is None:
            return False, mo.callout(mo.md("✏️ " + t("not_started")), kind="neutral")
        _lines, _ok = [], True
        _home_ok = a0 is not None and np.allclose(a0, [0, 30, 105] * 6, atol=0.01)
        _ok &= _home_ok
        _lines.append(("✓ " if _home_ok else "✗ ") + t("rt_home"))
        _fail_ok = a1 is None and leg1 in ("R1", "R2", "R3", "L1", "L2", "L3")
        _ok &= _fail_ok
        _lines.append(("✓ " if _fail_ok else "✗ ") + t("rt_fail").format(leg=leg1))
        _rng = np.random.default_rng(11)
        _n, _solved, _worst = 1000, 0, 0.0
        for _ in range(_n):
            _p = np.r_[_rng.uniform(-30, 30, 3), _rng.uniform(-8, 8, 3)]
            _a, _ = body_ik(_p)
            if _a is None:
                continue
            _solved += 1
            _worst = max(_worst, float(np.max(np.linalg.norm(_world_feet(np.asarray(_a, dtype=float), _p) - FEET, axis=1))))
        _rt_ok = _solved > 900 and _worst < 1e-6
        _ok &= _rt_ok
        _lines.append(("✓ " if _rt_ok else "✗ ") + t("rt_res").format(s=_solved, n=_n, w=_worst))
        return _ok, verdict(_ok, [("✅ " if _ok else "❌ ") + t("rt_head")] + _lines)

    ok2, _view = _run()
    _view
    return (ok2,)


@app.cell(hide_code=True)
def _(mo, t):
    mo.vstack([mo.md(t("ex3_md")), mo.accordion({t("hint") + " 1": mo.md(t("ex3_h1")), t("hint") + " 2": mo.md(t("ex3_h2")), t("answer"): mo.md(t("ex3_a"))})])
    return


@app.cell
def _(body_ik, np):
    def axis_range(axis, step=0.5, limit=200):
        """Move the body along ONE pose axis (0-5), the other five at 0. Returns (lo, hi): the farthest
        values in each direction, in steps of `step`, for which body_ik() still succeeds."""
        # ✏️ YOUR CODE HERE
        return None
    return (axis_range,)


@app.cell(hide_code=True)
def _(axis_range, body_ik, check, mo, np, t):
    ok3, _view = check(axis_range, [((0,), (-94.0, 94.0), "x (mm)"), ((1,), (-85.5, 85.5), "y (mm)"), ((2,), (-58.0, 91.0), "z (mm)"),
                                    ((3,), (-15.0, 15.0), "roll (°)"), ((4,), (-17.0, 17.0), "pitch (°)"), ((5,), (-29.5, 29.5), "yaw (°)")], tol=0.01)

    def _region(z):
        g = np.arange(-27, 27.1, 1.5)
        W, c, m = 200, 200 / len(g), 26
        out = [f"<svg viewBox='0 0 {W + m + 4} {W + 34}' style='width:100%;max-width:236px;font:10px monospace'>"]
        for i, p in enumerate(g[::-1]):
            for j, r in enumerate(g):
                ok = body_ik([0, 0, z, r, p, 0])[0] is not None
                out.append(f"<rect x='{m + j * c:.1f}' y='{i * c:.1f}' width='{c + 0.4:.1f}' height='{c + 0.4:.1f}' fill='{'#2a6fb0' if ok else '#8882'}'/>")
        out.append(f"<line x1='{m + W / 2}' y1='0' x2='{m + W / 2}' y2='{W}' stroke='#fff6'/><line x1='{m}' y1='{W / 2}' x2='{m + W}' y2='{W / 2}' stroke='#fff6'/>"
                   f"<g fill='currentColor' opacity='.75'><text x='{m}' y='{W + 11}'>−27</text><text x='{m + W}' y='{W + 11}' text-anchor='end'>+27</text>"
                   f"<text x='{m + W / 2}' y='{W + 11}' text-anchor='middle'>roll →</text>"
                   f"<text x='{m - 3}' y='9' text-anchor='end'>+27</text><text x='{m - 3}' y='{W}' text-anchor='end'>−27</text>"
                   f"<text transform='translate({m - 6},{W / 2}) rotate(-90)' text-anchor='middle'>pitch →</text></g>"
                   f"<text x='{m + W / 2}' y='{W + 28}' text-anchor='middle' fill='currentColor' font-size='11'>z = {z:+d} mm</text></svg>")
        return mo.Html("".join(out))

    _out = mo.vstack([_view, mo.md(t("region_md")), mo.hstack([_region(-20), _region(0), _region(20)], justify="start", wrap=True)]) if ok3 else _view
    _out
    return (ok3,)


@app.cell(hide_code=True)
def _(mo, t):
    mo.vstack([mo.md(t("ex4_md")), mo.accordion({t("hint") + " 1": mo.md(t("ex4_h1")), t("hint") + " 2": mo.md(t("ex4_h2")), t("answer"): mo.md(t("ex4_a"))})])
    return


@app.cell
def _(LEGS, body_ik, np):
    def make_plan(dance, seconds, cap=100, fps=50):
        """Sample dance(t) at fps for `seconds`. Returns (plan, None) with plan of shape (N, 18),
        or (None, reason) as soon as a pose can't be reached or a joint would turn faster than cap °/s."""
        # ✏️ YOUR CODE HERE
        return None, None
    return (make_plan,)


@app.cell(hide_code=True)
def _(make_plan, mo, np, t, verdict):
    def _gentle(tt):
        w = 2 * np.pi * 0.2
        return np.array([15 * np.sin(w * tt), 10 * np.sin(2 * w * tt), 8 * np.sin(1.5 * w * tt), 4 * np.sin(w * tt), 4 * np.sin(2 * w * tt), 6 * np.sin(w * tt + 1)])

    def _fast(tt):
        return np.array([0, 0, 0, 10 * np.sin(2 * np.pi * tt), 0, 0])

    def _far(tt):
        return np.array([0, 0, 0, 25 * np.sin(2 * np.pi * 0.1 * tt), 0, 0])

    def _run():
        try:
            p1, r1 = make_plan(_gentle, 10)
            p2, r2 = make_plan(_fast, 10)
            p3, r3 = make_plan(_far, 10)
        except Exception as e:
            return False, verdict(False, [f"❌ error: {type(e).__name__}: {e}"])
        if p1 is None and r1 is None:
            return False, mo.callout(mo.md("✏️ " + t("not_started")), kind="neutral")
        c1 = p1 is not None and np.shape(p1) == (501, 18) and r1 is None
        c2 = p2 is None and isinstance(r2, str) and "°/s" in r2
        c3 = p3 is None and isinstance(r3, str)
        _peak = float(np.max(np.abs(np.diff(np.asarray(p1), axis=0))) * 50) if c1 else 0
        _ok = c1 and c2 and c3
        return _ok, verdict(_ok, [("✅ " if _ok else "❌ ") + t("plan_head"),
                                  ("✓ " if c1 else "✗ ") + t("plan_1").format(s=np.shape(p1) if p1 is not None else None, p=_peak),
                                  ("✓ " if c2 else "✗ ") + t("plan_2").format(r=r2),
                                  ("✓ " if c3 else "✗ ") + t("plan_3").format(r=r3)])

    ok4, _view = _run()
    _view
    return (ok4,)


@app.cell(hide_code=True)
def _(mo, t):
    mo.md(t("r1_md"))
    return


@app.cell
def _(np):
    # ✏️ Your dance: pose(t) = (x, y, z, roll, pitch, yaw) in mm and degrees. Change anything, then run.
    DANCE_SECONDS = 12

    def my_dance(t):
        w = 2 * np.pi * 0.25                          # 0.25 Hz: one cycle every 4 s
        return np.array([0, 0, 15 * np.sin(w * t),   # bob up and down 15 mm
                         0, 6 * np.sin(w * t + np.pi / 2), 0])   # and nod, a quarter cycle ahead
    return DANCE_SECONDS, my_dance


@app.cell(hide_code=True)
def _(DANCE_SECONDS, FEET, MOUNTS, fk, make_plan, mo, my_dance, np, ok1, ok2, ok3, ok4, player, rot, t):
    if not (ok1 and ok2 and ok3 and ok4):
        dance_plan = None
        _out = mo.callout(mo.md("🔒 " + t("r_locked")), kind="neutral")
    elif DANCE_SECONDS < 10:
        dance_plan = None
        _out = mo.callout(mo.md(t("r1_short")), kind="warn")
    else:
        dance_plan, _why = make_plan(my_dance, DANCE_SECONDS)
        if dance_plan is None:
            _out = mo.callout(mo.md(t("r1_refused").format(r=_why)), kind="danger")
        else:
            _plan = np.asarray(dance_plan, dtype=float)
            _poses = [np.asarray(my_dance(k / 50), dtype=float) for k in range(len(_plan))]
            _slip = 0.0
            for _a, _p in zip(_plan[::10], _poses[::10]):
                _R = rot(*_p[3:])
                for _i, (_mx, _my, _al) in enumerate(MOUNTS):
                    _f = fk(*_a[3 * _i: 3 * _i + 3]); _c, _s = np.cos(np.radians(_al)), np.sin(np.radians(_al))
                    _w = _R @ np.array([_mx + _c * _f[0] - _s * _f[1], _my + _s * _f[0] + _c * _f[1], _f[2]]) + _p[:3]
                    _slip = max(_slip, float(np.linalg.norm(_w - FEET[_i])))
            _peak = float(np.max(np.abs(np.diff(_plan, axis=0))) * 50)
            _cfg = {"mode": "hex", "angles": [[[round(float(v), 2) for v in row[3 * i: 3 * i + 3]] for i in range(6)] for row in _plan],
                    "poses": [[round(float(v), 2) for v in p] for p in _poses], "fps": 50}
            _out = mo.vstack([player(_cfg, 420), mo.callout(mo.md(t("r1_done").format(n=len(_plan), p=_peak, s=_slip)), kind="success")])
    _out
    return (dance_plan,)


@app.cell(hide_code=True)
def _(IN_BROWSER, mo, t):
    robot_on = mo.ui.switch(label=t("robot_switch"))
    send = mo.ui.run_button(label=t("robot_send"))
    mo.vstack([mo.md(t("robot_md")),
               mo.callout(mo.md(t("robot_browser")), kind="neutral") if IN_BROWSER else mo.hstack([robot_on, send], justify="start")])
    return robot_on, send


@app.cell(hide_code=True)
def _(IN_BROWSER, dance_plan, mo, np, robot_on, send, t):
    mo.stop(IN_BROWSER or not send.value)
    mo.stop(not robot_on.value, mo.callout(mo.md(t("robot_need_switch")), kind="warn"))
    mo.stop(dance_plan is None, mo.callout(mo.md(t("robot_need_plan")), kind="danger"))

    import pathlib, sys as _sys
    _code_dir = pathlib.Path(mo.notebook_dir()).resolve().parents[1]           # .../code
    if str(_code_dir) not in _sys.path:
        _sys.path.insert(0, str(_code_dir))
    from utils.link import Link

    _home = np.array([0, 30, 105] * 6, dtype=float)
    _link = Link()
    try:
        _link.move_to(_home, 2)
        _link.play(np.asarray(dance_plan, dtype=float))
        _link.move_to(_home, 1.5)
    finally:
        _link.close()
    mo.callout(mo.md(t("robot_done").format(n=len(dance_plan))), kind="success")
    return


@app.cell(hide_code=True)
def _(mo, t):
    mo.md(t("outro"))
    return


@app.cell(hide_code=True)
def _(mo, np, t):
    def _fmt(v):
        if v is None:
            return "None"
        if isinstance(v, str):
            return v
        if isinstance(v, (bool, np.bool_)):
            return str(bool(v))
        if isinstance(v, (tuple, list)) and any(isinstance(x, (bool, np.bool_)) for x in v):
            return "(" + ", ".join(_fmt(x) for x in v) + ")"
        try:
            a = np.asarray(v, dtype=float)
        except (TypeError, ValueError):
            return str(v)
        num = lambda x: "0" if abs(x) < 5e-10 else f"{x:.6g}"
        return num(float(a)) if a.ndim == 0 else "[" + ", ".join(num(float(x)) for x in a.ravel()) + "]"

    def check(fn, cases, tol=0.01, radians_hint=False):
        """Run fn on each case and compare with the expected value.
        A case is (args, expected) or (args, expected, label). Expected None means 'should return None'."""
        rows, passed, rad = [], 0, False
        for case in cases:
            args, exp = case[0], case[1]
            label = case[2] if len(case) > 2 else ", ".join(str(a) for a in args)
            try:
                got = fn(*args)
            except Exception as e:
                got = f"error: {type(e).__name__}: {e}"
            ok = False
            if isinstance(got, str):
                pass
            elif exp is None:
                ok = got is None
            elif got is not None:
                try:
                    g = np.atleast_1d(np.asarray(got, dtype=float))
                    e = np.atleast_1d(np.asarray(exp, dtype=float))
                    ok = g.shape == e.shape and bool(np.all(np.abs(g - e) <= tol))
                    if radians_hint and g.shape == e.shape and np.all(np.abs(np.degrees(g) - e) <= tol) and np.any(np.abs(e) > tol):
                        rad = True
                except (TypeError, ValueError):
                    ok = False
            passed += ok
            rows.append((label, _fmt(exp), _fmt(got), "✓" if ok else "✗"))
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
        kind = "success" if all_ok else ("neutral" if head.startswith("✏️") else "danger")
        return all_ok, mo.callout(mo.md(head + "\n\n" + table), kind=kind)

    def verdict(ok, lines):
        """A callout for checks that are not a simple table."""
        return mo.callout(mo.md("\n\n".join(lines)), kind="success" if ok else "danger")
    return check, verdict


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
  // draw one frame. opts: {legs: indices, pose, angles:[[t1,t2,t3]|null...], trails, marks, gridOff, under, az, el, scale, body}
  function draw(ctx, W, H, o, col) {
    const az = o.az, el = o.el, s = o.scale, cx = W / 2 + (o.ox || 0), cy = H * (o.cy || 0.62);
    const P = p => { const xr = p[0] * Math.cos(az) - p[1] * Math.sin(az), yr = p[0] * Math.sin(az) + p[1] * Math.cos(az); return [cx + s * xr, cy - s * ((p[2] + (o.ground || HOME_H)) * Math.cos(el) + yr * Math.sin(el))]; };
    ctx.clearRect(0, 0, W, H);
    // ground grid
    ctx.strokeStyle = col.grid; ctx.lineWidth = 1;
    const g = o.gridR || 360, gz = -(o.ground || HOME_H), go = o.gridOff || [0, 0]; // gridOff scrolls the grid (follow camera)
    const gx = ((go[0] % 40) + 40) % 40, gy = ((go[1] % 40) + 40) % 40;
    for (let k = -g - 40; k <= g; k += 40) {
      const x = k + gx, y = k + gy; let a, b;
      if (x >= -g && x <= g) { a = P([x, -g, gz]); b = P([x, g, gz]); ctx.beginPath(); ctx.moveTo(a[0], a[1]); ctx.lineTo(b[0], b[1]); ctx.stroke(); }
      if (y >= -g && y <= g) { a = P([-g, y, gz]); b = P([g, y, gz]); ctx.beginPath(); ctx.moveTo(a[0], a[1]); ctx.lineTo(b[0], b[1]); ctx.stroke(); }
    }
    // marks: ground points such as footprints, [x, y, z, alpha]
    (o.marks || []).forEach(m => { const q = P(m); ctx.globalAlpha = m[3] == null ? 0.5 : m[3]; ctx.fillStyle = o.markColor || col.muted; ctx.beginPath(); ctx.ellipse(q[0], q[1], 5, 2.6, 0, 0, 7); ctx.fill(); });
    ctx.globalAlpha = 1;
    if (o.under) o.under(ctx, P); // extra ground drawing, below the robot
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
        """Animate the leg or the hexapod from joint angles (the JS only does forward kinematics).
        cfg: mode 'leg' | 'hex' | 'walk', angles per frame, optional poses / target / prints, fps."""
        html = """<!doctype html><html><head><meta charset='utf-8'><style>
        :root{--ink:#16202a;--muted:#5b6875;--grid:#e4e9ee;--accent:#d9771f;--body:#e9edf1;--bg:#fff}
        @media (prefers-color-scheme: dark){:root{--ink:#e3e9ef;--muted:#98a5b2;--grid:#26313c;--accent:#f0954a;--body:#26323e;--bg:#17202a}}
        html,body{margin:0;background:var(--bg);font:12px monospace;color:var(--muted)}
        canvas{width:100%;height:calc(100vh - 6px);display:block;cursor:grab;touch-action:none}
        #lbl{position:absolute;left:10px;top:8px;white-space:pre}</style></head><body><div id='lbl'></div><canvas id='c'></canvas><script>"""
        html += HEXVIEW_JS
        html += "\nconst CFG=" + json.dumps(cfg) + ";\n"
        html += r"""
        const cv=document.getElementById('c'),ctx=cv.getContext('2d'),lbl=document.getElementById('lbl');
        const css=n=>getComputedStyle(document.documentElement).getPropertyValue(n).trim();
        const C={ink:css('--ink'),muted:css('--muted'),grid:css('--grid'),accent:css('--accent'),body:css('--body')};
        function fit(){const r=cv.getBoundingClientRect();cv.width=r.width*devicePixelRatio;cv.height=r.height*devicePixelRatio;}
        fit();addEventListener('resize',fit);
        let az=CFG.mode==='leg'?-0.55:-0.75,lx=null;
        cv.onpointerdown=e=>{lx=e.clientX;cv.setPointerCapture(e.pointerId)};cv.onpointermove=e=>{if(lx!=null){az+=(e.clientX-lx)*0.01;lx=e.clientX}};cv.onpointerup=()=>lx=null;
        const N=CFG.angles.length,trail=[],t0=performance.now(),LEG=[{m:[0,0],a:0}],ZERO=[0,0,0,0,0,0];
        function frame(now){
          const k=N>1?Math.max(0,Math.floor((now-t0)/1000*CFG.fps))%N:0;
          if(k===0&&trail.length>N/2)trail.length=0;
          const s=Math.min(cv.width,cv.height*1.35)/(CFG.mode==='leg'?230:(CFG.span||620));
          if(CFG.mode==='leg'){
            const pts=HX.draw(ctx,cv.width,cv.height,{legDefs:LEG,angles:CFG.angles[k],pose:ZERO,az,el:0.55,scale:s,body:false,ox:-s*95,cy:CFG.cy||0.78,gridR:200,
              trails:[trail],targets:CFG.target?[CFG.target.concat([CFG.target[0]])]:[]},C);
            if(pts[0]&&CFG.target)trail.push(pts[0][3]);
            lbl.textContent=(CFG.labels?CFG.labels[k]:'frame '+k+'/'+N)+(CFG.angles[k][0]?'':'  ✗ None');
          }else if(CFG.mode==='walk'){
            const P=CFG.poses[k],bx=P[0],by=P[1],marks=[];
            (CFG.prints||[]).forEach(q=>{if(q[2]<=k)marks.push([q[0]-bx,q[1]-by,-HX.HOME_H,0.55])});
            HX.draw(ctx,cv.width,cv.height,{legs:[0,1,2,3,4,5],angles:CFG.angles[k],pose:[0,0,P[2],P[3],P[4],P[5]],az,el:0.5,scale:s,body:true,cy:0.62,
              marks,gridOff:[-bx,-by],gridR:440},C);
            lbl.textContent=(CFG.labels?CFG.labels[k]:'');
          }else{
            HX.draw(ctx,cv.width,cv.height,{legs:[0,1,2,3,4,5],angles:CFG.angles[k],pose:CFG.poses?CFG.poses[k]:ZERO,az,el:0.5,scale:s,body:true,cy:0.62,
              legColor:CFG.legColor||null},C);
            lbl.textContent=CFG.labels?CFG.labels[k]:(N>1?'t = '+(k/CFG.fps).toFixed(2)+' s':'');
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
            "hint": 'Hint',
            "answer": 'Answer (try the hints first!)',
            "th": '| input | expected | yours | |',
            "pass": 'All {n} tests passed.',
            "fail": '{p}/{n} tests passed.',
            "not_started": 'Not started yet: write your code in the cell above and run it.',
            "rad_hint": 'Your numbers look like **radians**. Convert with `np.degrees(...)`.',
            "all_unlocked": 'All checkpoints passed. Rewards unlocked below!',
            "locked_n": '{n} checkpoint(s) left before the rewards unlock.',
            "r_locked": 'Locked. Pass all checkpoints above to unlock.',
            "robot_browser": "This part only works when you run the notebook locally (`marimo edit ...`) with the robot plugged in. The browser can't open your serial port.",
            "robot_switch": 'Robot is connected and powered',
            "robot_need_switch": 'Turn on the switch first to confirm the robot is ready.',
            "crumb": 'Stage 5 · Body kinematics · practice',
            "intro": """# Keep the feet, move the body 🕺
    
    Stage 3 solved one leg in its own frame. Now all six feet stay planted on the floor while the **body** moves and turns, and for every pose of the body you need all 18 joint angles. That is `body_ik()`, built in **4 small pieces**: the change of frames, body IK with a round-trip test, how far the body can go, and a planner that checks every joint's speed before anything moves.
    
    How to work: edit the code cells marked ✏️, then run them (Ctrl/Cmd + Enter). The checker under each one updates on its own. If you're stuck, open the hints one at a time; the last one is the full answer. Pass all four to unlock **your own dance** on the simulated robot.""",
            "given_md": """## What you're given
    
    **Three frames.** Each describes positions from a different point of view (a **frame** is an origin plus three perpendicular axes):
    - **World**: fixed to the floor. The planted feet never move in it. Origin under the body's centre at home, x forward, y left, z up.
    - **Body**: glued to the robot's body, origin at its centre. When the body moves, this frame moves with it.
    - **Leg i**: origin at leg i's coxa axis, x pointing straight out along that leg. This is the frame Stage 3's `ik()` works in.
    
    **The pose** of the body is six numbers, `pose = (x, y, z, roll, pitch, yaw)`: where the body frame's origin is in the world (mm), and how it is turned (degrees). **Roll** turns about the forward x axis (tilts sideways), **pitch** about the y axis (nods), **yaw** about the vertical z axis (turns left/right). At home all six are 0.
    
    **Per leg**, `MOUNTS[i] = (mx, my, α)`: where leg i's coxa sits in the body frame (mm) and the direction its x axis points (α, alpha, degrees from the body's forward axis). `FEET[i]` is where foot i is planted in the world: 162 mm straight out from its coxa and 89.5 mm down. `fk` and `ik` are Stages 1 and 3; `LEGS` names the legs.""",
            "ex1_md": """## ✏️ 1 · Change of frames
    
    **A rotation matrix.** Turning a vector by an angle is a matrix product R · v. The three basic turns, by an angle a (c = cos a, s = sin a):
    
    ```
             ⎡ 1  0   0 ⎤          ⎡  c  0  s ⎤          ⎡ c  −s  0 ⎤
    Rx(a) =  ⎢ 0  c  −s ⎥  Ry(a) = ⎢  0  1  0 ⎥  Rz(a) = ⎢ s   c  0 ⎥
             ⎣ 0  s   c ⎦          ⎣ −s 0  c ⎦          ⎣ 0   0  1 ⎦
    ```
    
    Each **column** is where one axis ends up: column 1 of Rz(a) is the x axis turned by a, (c, s, 0). Our body orientation is **R = Rz(yaw) · Ry(pitch) · Rx(roll)**. R takes a direction measured in the body frame and gives the same direction in the world. Its **transpose** Rᵀ (rows and columns swapped) undoes it: for a rotation, Rᵀ = R⁻¹.
    
    **From world to leg frame**, in three steps. Let t = (x, y, z) be the body's position and m = (mx, my, 0) the coxa's position in the body:
    1. **World → body**: subtract the body's position, then undo its turn: pᴮ = Rᵀ · (f − t).
    2. **Body → coxa**: subtract the coxa's position: d = pᴮ − m.
    3. **Coxa → leg frame**: undo the leg's direction α, which is a turn by −α about z: pᴸ = Rz(−α) · d.
    
    All together, the page's formula: **pᴸᵢ = Rz(−αᵢ) · ( Rᵀ · (fᵢ − t) − mᵢ )**.
    
    Write `rot(roll, pitch, yaw)` and `to_leg_frame(f, pose, i)`. Test yourself: at the home pose, every foot must come out at (162, 0, −89.5).""",
            "ex1_h1": 'In numpy, `@` multiplies matrices and `R.T` is the transpose. Build Rx, Ry, Rz with `np.array([[...], [...], [...]])` (angles in radians), then `return Rz @ Ry @ Rx`.',
            "ex1_h2": "Rz(−α) · d written out: cos(−α) = cos α and sin(−α) = −sin α, so x' = cos α · dx + sin α · dy, y' = −sin α · dx + cos α · dy, z' = dz.",
            "ex1_a": """```python
    def rot(roll, pitch, yaw):
        r, p, y = np.radians([roll, pitch, yaw])
        Rx = np.array([[1, 0, 0], [0, np.cos(r), -np.sin(r)], [0, np.sin(r), np.cos(r)]])
        Ry = np.array([[np.cos(p), 0, np.sin(p)], [0, 1, 0], [-np.sin(p), 0, np.cos(p)]])
        Rz = np.array([[np.cos(y), -np.sin(y), 0], [np.sin(y), np.cos(y), 0], [0, 0, 1]])
        return Rz @ Ry @ Rx
    
    def to_leg_frame(f, pose, i):
        R = rot(*pose[3:])
        pb = R.T @ (np.asarray(f, dtype=float) - np.asarray(pose[:3], dtype=float))
        mx, my, a = MOUNTS[i]
        d = pb - np.array([mx, my, 0])
        c, s = np.cos(np.radians(a)), np.sin(np.radians(a))
        return np.array([c * d[0] + s * d[1], -s * d[0] + c * d[1], d[2]])
    ```""",
            "ex2_md": """## ✏️ 2 · Body IK, and a round trip
    
    Now the whole robot: for each leg i, move its planted foot `FEET[i]` into leg i's frame with your `to_leg_frame`, and ask `ik()` for the three angles. If any leg can't reach (ik returns None), the pose is impossible: stop and say which leg.
    
    Write `body_ik(pose)` that returns `(angles, None)`, with all 18 angles in one array (R1 coxa, femur, tibia, then R2, …, L3), or `(None, leg_name)`.
    
    The checker then runs a **round trip**, the same idea as in Stage 3: 1,000 random poses (±30 mm, ±8°). For each one that body_ik solves, it runs everything **forwards** (your angles → fk → leg frame → body → world) and measures where the six feet really end up. If your body IK is right, every foot lands exactly on its planted spot.""",
            "ex2_h1": 'Loop `for i in range(6)`, compute `a = ik(*to_leg_frame(FEET[i], pose, i))`; if `a is None`, return `None, LEGS[i]`; otherwise `out.extend(a)`. At the end return `np.array(out), None`.',
            "ex2_a": """```python
    out = []
    for i in range(6):
        a = ik(*to_leg_frame(FEET[i], pose, i))
        if a is None:
            return None, LEGS[i]
        out.extend(a)
    return np.array(out), None
    ```""",
            "ex2_wait": 'Finish checkpoint 1 first.',
            "rt_head": 'body_ik() round trip',
            "rt_home": 'home pose gives (0°, 30°, 105°) on every leg',
            "rt_fail": 'roll 30° is refused (first failing leg: {leg})',
            "rt_res": 'solved {s}/{n} random poses; feet returned to their spots within **{w:.1e} mm**',
            "ex3_md": """## ✏️ 3 · How far can the body go?
    
    Every pose axis has a range: push the body further and the **first** joint to hit its limit (or the first foot out of reach) ends it. Find each range by scanning:
    
    - Start at 0 on one axis, all other five axes at 0.
    - Step outward by `step` (0.5 mm or 0.5°) and try body_ik at each new value.
    - The range ends at the **last value that worked**. Do this once in the negative direction and once in the positive direction, and stop at `limit` in case nothing ever fails.
    
    Write `axis_range(axis)` that returns `(lo, hi)`. Axis numbers follow the pose: 0 = x, 1 = y, 2 = z, 3 = roll, 4 = pitch, 5 = yaw.""",
            "ex3_h1": 'An outer loop over `sign in (-1, 1)`; an inner `while` loop that builds `pose = np.zeros(6)`, sets `pose[axis] = sign * (abs(v) + step)`, and stops when `body_ik(pose)[0] is None`.',
            "ex3_h2": 'Keep the last good value in v, and start each direction with v = 0.0. Return `(ends[0], ends[1])` with the negative end first.',
            "ex3_a": """```python
    ends = []
    for sign in (-1, 1):
        v = 0.0
        while abs(v) + step <= limit:
            pose = np.zeros(6)
            pose[axis] = sign * (abs(v) + step)
            if body_ik(pose)[0] is None:
                break
            v = pose[axis]
        ends.append(v)
    return ends[0], ends[1]
    ```""",
            "region_md": "Roll alone reaches ±15° and pitch alone ±17°, but what about both at once? Below, your `body_ik` tries every combination (horizontal: roll, vertical: pitch, both from −27° to +27°) at three body heights. Blue = all 18 joints legal. At home height the region is roughly a **hexagon**: each of its six sides is one leg's femur reaching its limit first (R2 on the right side, L2 on the left, the other four legs on the slanted sides), and each corner is where two legs give up together. Raising the body by 20 mm makes it bigger (every femur starts further from its limit); lowering it makes it smaller.",
            "ex4_md": """## ✏️ 4 · A safe dance planner
    
    A **dance** is a function `dance(t)` that returns a pose for every time t (seconds). The robot takes a new frame every Δt = 1/50 s, so the planner samples t = 0, 0.02, 0.04, … up to `seconds`, and runs body_ik on each sample.
    
    Two things can go wrong, and both must be caught **before** anything moves:
    - **Reach**: some pose is impossible (body_ik returns None).
    - **Speed**: a joint's angular speed is the change in its angle between two frames divided by the time between them: speed ≈ |θ(t + Δt) − θ(t)| / Δt = |Δθ| · fps. If any joint would turn faster than `cap` (100°/s), the servo can't keep up (Stage 0).
    
    Write `make_plan(dance, seconds)` that returns `(plan, None)`, a (N, 18) array with one row per frame, or `(None, reason)` with a short, readable reason as soon as something fails. Write the speed reason with **°/s** in it, like `"t = 0.02 s: L2 joint 2 at 195°/s"`: the checker looks for it.""",
            "ex4_h1": 'Frames k = 0 … round(seconds · fps), time tt = k / fps (not k: one of our real bugs). After body_ik, compare with the previous row: `speed = np.abs(a - rows[-1]) * fps`.',
            "ex4_h2": "`j = int(np.argmax(speed))` finds the fastest joint; joint j belongs to leg `LEGS[j // 3]`. Test the check with something that should fail: that's how we found a speed check that never fired.",
            "ex4_a": """```python
    rows = []
    for k in range(int(round(seconds * fps)) + 1):
        tt = k / fps
        a, leg = body_ik(dance(tt))
        if a is None:
            return None, f"t = {tt:.2f} s: leg {leg} can't reach its foot"
        if rows:
            speed = np.abs(a - rows[-1]) * fps
            j = int(np.argmax(speed))
            if speed[j] > cap:
                return None, f"t = {tt:.2f} s: {LEGS[j // 3]} joint {j % 3 + 1} at {speed[j]:.0f}°/s"
        rows.append(a)
    return np.array(rows), None
    ```""",
            "plan_head": 'make_plan() on three test dances',
            "plan_1": 'a gentle 10 s dance is planned: shape {s}, peak {p:.0f}°/s',
            "plan_2": 'roll ±10° at 1 Hz is refused for speed: "{r}"',
            "plan_3": 'roll ±25° is refused for reach: "{r}"',
            "r1_md": """## ★ Reward · Your dance
    
    Edit `my_dance(t)` below: any pose as a function of time, at least 10 seconds long. Ideas: sway sideways with `y`, circle the body with x = A·cos(wt), y = A·sin(wt), turn with yaw, or combine. Your `make_plan` checks it; if it passes, it plays on the simulated robot with the feet planted. If it's refused, the reason tells you what to slow down or shrink.""",
            "r1_short": 'Make DANCE_SECONDS at least 10.',
            "r1_refused": 'make_plan() refused your dance: **{r}**. Make it smaller or slower and run the cell again.',
            "r1_done": '**Your dance is planned and playing:** {n} frames, peak joint speed **{p:.0f}°/s** (cap 100), feet stayed within **{s:.1e} mm** of their spots.',
            "robot_md": """## 🤖 Bonus · Dance on the real robot
    
    The same plan, sent through `utils/link.py` at 50 Hz. The robot moves to home, dances, and returns home. Put a coin next to each foot first: if body IK is right and the feet don't slip, none of them should move. **Put the robot on the floor with space around it; keep the USB cable slack.**""",
            "robot_send": '▶ Send my dance',
            "robot_need_plan": 'Finish the reward first so there is a plan to send.',
            "robot_done": 'Done: sent {n} frames. 🎉 Check the coins.',
            "outro": """## What you just learned
    - A body pose is **six numbers**; a rotation is a **3×3 matrix** whose columns are the turned axes, and Rᵀ undoes it.
    - Body IK = **change of frames** (world → body → coxa → leg) + six ordinary leg IKs.
    - The body's range is set by the **first leg to give up**; combined roll and pitch form a hexagon.
    - Plan first, then move: check **reach and joint speed** on every frame before sending anything.
    
    **Next: Stage 6 · Gait.** Lift the feet one group at a time and walk.""",
        },
        "zh": {
            "hint": '提示',
            "answer": '答案（先试试提示！）',
            "th": '| 输入 | 期望 | 你的结果 | |',
            "pass": '{n} 个测试全部通过。',
            "fail": '通过 {p}/{n} 个测试。',
            "not_started": '还没开始：在上面的格子里写代码并运行。',
            "rad_hint": '你的结果看起来是**弧度**。用 `np.degrees(...)` 转换。',
            "all_unlocked": '全部检查点通过，奖励已在下方解锁！',
            "locked_n": '还差 {n} 个检查点解锁奖励。',
            "r_locked": '未解锁。先通过上面所有检查点。',
            "robot_browser": '这部分只能在本地运行 notebook（`marimo edit ...`）并插上机器人时使用。浏览器打不开你的串口。',
            "robot_switch": '机器人已连接并通电',
            "robot_need_switch": '先打开开关，确认机器人已准备好。',
            "crumb": '阶段 5 · 机身运动学 · 练习',
            "intro": """# 脚不动，身体动 🕺
    
    阶段 3 在一条腿自己的坐标系里求解了这条腿。现在六只脚都踩在地上不动，**机身**移动和转动，对机身的每个姿态你都需要 18 个关节角。这就是 `body_ik()`，分 **4 小块**来做：坐标系变换，带回环测试的机身 IK，机身能动多远，以及一个在任何东西动起来之前先检查每个关节速度的规划器。
    
    怎么做：修改标了 ✏️ 的代码格子，然后运行（Ctrl/Cmd + Enter）。每个格子下面的检查器会自动更新。卡住了就一条一条展开提示，最后一条是完整答案。四个全部通过后，解锁在模拟机器人上跳**你自己编的舞**。""",
            "given_md": """## 已经给你的东西
    
    **三个坐标系。** 每个都从不同的视角描述位置（**坐标系**就是一个原点加三根互相垂直的轴）：
    - **世界系**：固定在地面上。踩住的脚在这里永远不动。原点在 home 时机身中心的正下方，x 向前，y 向左，z 向上。
    - **机身系**：粘在机器人身体上，原点在机身中心。机身动，它跟着动。
    - **第 i 条腿的坐标系**：原点在第 i 条腿的 coxa 轴，x 沿这条腿笔直向外。阶段 3 的 `ik()` 就在这个坐标系里工作。
    
    **机身姿态**是六个数，`pose = (x, y, z, roll, pitch, yaw)`：机身坐标系的原点在世界系中的位置（mm），以及它转了多少（度）。**Roll**（横滚）绕向前的 x 轴转（侧倾），**pitch**（俯仰）绕 y 轴转（点头），**yaw**（偏航）绕竖直的 z 轴转（左右转）。home 时六个都是 0。
    
    **每条腿**，`MOUNTS[i] = (mx, my, α)`：第 i 条腿的 coxa 在机身系中的位置（mm），以及它的 x 轴指向的方向（α，alpha，从机身前向量起的度数）。`FEET[i]` 是第 i 只脚在世界系中踩住的位置：从它的 coxa 笔直向外 162 mm，向下 89.5 mm。`fk` 和 `ik` 来自阶段 1 和 3；`LEGS` 是腿的名字。""",
            "ex1_md": """## ✏️ 1 · 坐标系变换
    
    **旋转矩阵。** 把一个向量转过一个角度，就是一次矩阵乘法 R · v。三种基本转动，转角为 a（c = cos a，s = sin a）：
    
    ```
             ⎡ 1  0   0 ⎤          ⎡  c  0  s ⎤          ⎡ c  −s  0 ⎤
    Rx(a) =  ⎢ 0  c  −s ⎥  Ry(a) = ⎢  0  1  0 ⎥  Rz(a) = ⎢ s   c  0 ⎥
             ⎣ 0  s   c ⎦          ⎣ −s 0  c ⎦          ⎣ 0   0  1 ⎦
    ```
    
    每一**列**是一根轴转过去以后的位置：Rz(a) 的第 1 列就是转了 a 的 x 轴 (c, s, 0)。我们的机身朝向是 **R = Rz(yaw) · Ry(pitch) · Rx(roll)**。R 把在机身系中量的方向变成世界系中的同一个方向。它的**转置** Rᵀ（行列互换）把它撤销：对旋转矩阵，Rᵀ = R⁻¹。
    
    **从世界系到腿坐标系**，分三步。设 t = (x, y, z) 是机身位置，m = (mx, my, 0) 是 coxa 在机身中的位置：
    1. **世界 → 机身**：减去机身位置，再撤销它的转动：pᴮ = Rᵀ · (f − t)。
    2. **机身 → coxa**：减去 coxa 的位置：d = pᴮ − m。
    3. **coxa → 腿坐标系**：撤销腿的方向 α，即绕 z 转 −α：pᴸ = Rz(−α) · d。
    
    合起来就是页面上的公式：**pᴸᵢ = Rz(−αᵢ) · ( Rᵀ · (fᵢ − t) − mᵢ )**。
    
    写 `rot(roll, pitch, yaw)` 和 `to_leg_frame(f, pose, i)`。自测：在 home 姿态，每只脚都必须得到 (162, 0, −89.5)。""",
            "ex1_h1": '在 numpy 里 `@` 是矩阵乘法，`R.T` 是转置。用 `np.array([[...], [...], [...]])` 构造 Rx、Ry、Rz（角度用弧度），然后 `return Rz @ Ry @ Rx`。',
            "ex1_h2": "Rz(−α) · d 展开：cos(−α) = cos α，sin(−α) = −sin α，所以 x' = cos α · dx + sin α · dy，y' = −sin α · dx + cos α · dy，z' = dz。",
            "ex1_a": """```python
    def rot(roll, pitch, yaw):
        r, p, y = np.radians([roll, pitch, yaw])
        Rx = np.array([[1, 0, 0], [0, np.cos(r), -np.sin(r)], [0, np.sin(r), np.cos(r)]])
        Ry = np.array([[np.cos(p), 0, np.sin(p)], [0, 1, 0], [-np.sin(p), 0, np.cos(p)]])
        Rz = np.array([[np.cos(y), -np.sin(y), 0], [np.sin(y), np.cos(y), 0], [0, 0, 1]])
        return Rz @ Ry @ Rx
    
    def to_leg_frame(f, pose, i):
        R = rot(*pose[3:])
        pb = R.T @ (np.asarray(f, dtype=float) - np.asarray(pose[:3], dtype=float))
        mx, my, a = MOUNTS[i]
        d = pb - np.array([mx, my, 0])
        c, s = np.cos(np.radians(a)), np.sin(np.radians(a))
        return np.array([c * d[0] + s * d[1], -s * d[0] + c * d[1], d[2]])
    ```""",
            "ex2_md": """## ✏️ 2 · 机身 IK 与回环测试
    
    现在是整只机器人：对每条腿 i，用你的 `to_leg_frame` 把它踩住的脚 `FEET[i]` 变到第 i 条腿的坐标系里，再让 `ik()` 求三个角。只要有一条腿够不到（ik 返回 None），这个姿态就不可能：停下来，并说明是哪条腿。
    
    写 `body_ik(pose)`，返回 `(angles, None)`，18 个角放在一个数组里（R1 的 coxa、femur、tibia，然后 R2，……，L3）；或者返回 `(None, 腿名)`。
    
    接着检查器跑一个**回环测试**，思路和阶段 3 一样：1000 个随机姿态（±30 mm，±8°）。对 body_ik 能解的每一个，把整条链**正着**算一遍（你的角 → fk → 腿坐标系 → 机身 → 世界），看六只脚实际到了哪里。如果你的机身 IK 正确，每只脚都正好落回它踩住的位置。""",
            "ex2_h1": '`for i in range(6)` 循环，计算 `a = ik(*to_leg_frame(FEET[i], pose, i))`；如果 `a is None` 就返回 `None, LEGS[i]`；否则 `out.extend(a)`。最后返回 `np.array(out), None`。',
            "ex2_a": """```python
    out = []
    for i in range(6):
        a = ik(*to_leg_frame(FEET[i], pose, i))
        if a is None:
            return None, LEGS[i]
        out.extend(a)
    return np.array(out), None
    ```""",
            "ex2_wait": '先完成检查点 1。',
            "rt_head": 'body_ik() 回环测试',
            "rt_home": 'home 姿态下每条腿都是 (0°, 30°, 105°)',
            "rt_fail": 'roll 30° 被拒绝（第一条失败的腿：{leg}）',
            "rt_res": '解出 {s}/{n} 个随机姿态；脚回到原位的误差在 **{w:.1e} mm** 以内',
            "ex3_md": """## ✏️ 3 · 机身能动多远？
    
    每个姿态轴都有一个范围：机身再往前推，**第一个**碰到限位的关节（或第一只够不到的脚）就决定了终点。用扫描来找每个范围：
    
    - 从某一根轴的 0 开始，其余五根轴都是 0。
    - 每次向外走 `step`（0.5 mm 或 0.5°），在每个新值上试一次 body_ik。
    - 范围终止于**最后一个成功的值**。负方向做一次，正方向做一次；如果一直不失败，到 `limit` 就停。
    
    写 `axis_range(axis)`，返回 `(lo, hi)`。轴的编号和 pose 一致：0 = x，1 = y，2 = z，3 = roll，4 = pitch，5 = yaw。""",
            "ex3_h1": '外层循环 `sign in (-1, 1)`；内层 `while` 循环构造 `pose = np.zeros(6)`，设 `pose[axis] = sign * (abs(v) + step)`，当 `body_ik(pose)[0] is None` 时停止。',
            "ex3_h2": '用 v 记住最后一个成功的值，每个方向开始时 v = 0.0。返回 `(ends[0], ends[1])`，负端在前。',
            "ex3_a": """```python
    ends = []
    for sign in (-1, 1):
        v = 0.0
        while abs(v) + step <= limit:
            pose = np.zeros(6)
            pose[axis] = sign * (abs(v) + step)
            if body_ik(pose)[0] is None:
                break
            v = pose[axis]
        ends.append(v)
    return ends[0], ends[1]
    ```""",
            "region_md": '单独 roll 能到 ±15°，单独 pitch 能到 ±17°，那两个同时呢？下面你的 `body_ik` 把所有组合都试一遍（横轴：roll，纵轴：pitch，都从 −27° 到 +27°），在三个机身高度上。蓝色 = 18 个关节都合法。在 home 高度，这个区域大致是个**六边形**：每条边对应一条腿的 femur 先碰到限位（右边是 R2，左边是 L2，另外四条腿各占一条斜边），每个角是两条腿同时到极限的地方。机身升高 20 mm 区域变大（每个 femur 一开始就离限位更远）；降低则变小。',
            "ex4_md": """## ✏️ 4 · 一个安全的舞蹈规划器
    
    **舞蹈**就是一个函数 `dance(t)`，对每个时刻 t（秒）返回一个姿态。机器人每 Δt = 1/50 s 取一帧，所以规划器在 t = 0、0.02、0.04、…… 直到 `seconds` 处采样，并对每个样本跑 body_ik。
    
    有两种情况会出问题，都必须在任何东西动起来**之前**发现：
    - **够不到**：某个姿态不可能（body_ik 返回 None）。
    - **太快**：关节的角速度就是相邻两帧之间角度的变化除以时间间隔：速度 ≈ |θ(t + Δt) − θ(t)| / Δt = |Δθ| · fps。只要有关节要转得比 `cap`（100°/s）还快，舵机就跟不上（阶段 0）。
    
    写 `make_plan(dance, seconds)`，返回 `(plan, None)`，一个 (N, 18) 的数组，每帧一行；或者一出问题就返回 `(None, reason)`，附一句简短易懂的原因。速度原因里要带 **°/s**，比如 `"t = 0.02 s: L2 joint 2 at 195°/s"`：检查器会找它。""",
            "ex4_h1": '帧 k = 0 … round(seconds · fps)，时间 tt = k / fps（不是 k：这是我们真实遇到过的 bug）。body_ik 之后和上一行比较：`speed = np.abs(a - rows[-1]) * fps`。',
            "ex4_h2": '`j = int(np.argmax(speed))` 找出最快的关节；关节 j 属于 `LEGS[j // 3]` 这条腿。用一个应该失败的例子测试你的检查：我们就是这样发现一个从来不会触发的速度检查的。',
            "ex4_a": """```python
    rows = []
    for k in range(int(round(seconds * fps)) + 1):
        tt = k / fps
        a, leg = body_ik(dance(tt))
        if a is None:
            return None, f"t = {tt:.2f} s: leg {leg} can't reach its foot"
        if rows:
            speed = np.abs(a - rows[-1]) * fps
            j = int(np.argmax(speed))
            if speed[j] > cap:
                return None, f"t = {tt:.2f} s: {LEGS[j // 3]} joint {j % 3 + 1} at {speed[j]:.0f}°/s"
        rows.append(a)
    return np.array(rows), None
    ```""",
            "plan_head": 'make_plan() 处理三段测试舞蹈',
            "plan_1": '一段温和的 10 s 舞蹈规划成功：形状 {s}，峰值 {p:.0f}°/s',
            "plan_2": '1 Hz、±10° 的 roll 因速度被拒绝："{r}"',
            "plan_3": '±25° 的 roll 因够不到被拒绝："{r}"',
            "r1_md": """## ★ 奖励 · 你的舞
    
    修改下面的 `my_dance(t)`：任意一个随时间变化的姿态，至少 10 秒。点子：用 `y` 左右摇摆，用 x = A·cos(wt)、y = A·sin(wt) 让机身画圈，用 yaw 转身，或者组合起来。你的 `make_plan` 会检查它；通过的话，它就在模拟机器人上播放，脚踩住不动。被拒绝的话，原因会告诉你该放慢什么、缩小什么。""",
            "r1_short": '把 DANCE_SECONDS 设为至少 10。',
            "r1_refused": 'make_plan() 拒绝了你的舞：**{r}**。改小或放慢，再运行一次这个格子。',
            "r1_done": '**你的舞已规划好并在播放：** {n} 帧，关节峰值速度 **{p:.0f}°/s**（上限 100），脚离原位不超过 **{s:.1e} mm**。',
            "robot_md": """## 🤖 附加 · 在真机器人上跳
    
    同一份规划，通过 `utils/link.py` 以 50 Hz 发送。机器人先到 home，跳舞，再回到 home。先在每只脚旁边放一枚硬币：如果机身 IK 正确、脚没有打滑，硬币都不应该被碰动。**把机器人放在四周有空间的地上；USB 线要留松。**""",
            "robot_send": '▶ 发送我的舞',
            "robot_need_plan": '先完成奖励部分，才有规划可以发送。',
            "robot_done": '完成：发送了 {n} 帧。🎉 看看硬币。',
            "outro": """## 你刚学到的
    - 机身姿态是**六个数**；转动是一个 **3×3 矩阵**，它的各列就是转过去的各根轴，Rᵀ 把它撤销。
    - 机身 IK = **坐标系变换**（世界 → 机身 → coxa → 腿）+ 六次普通的单腿 IK。
    - 机身的活动范围由**第一条放弃的腿**决定；roll 和 pitch 组合起来的可行区域是个六边形。
    - 先规划，再动：在发送任何东西之前，检查每一帧的**可达性和关节速度**。
    
    **下一步：阶段 6 · 步态。** 一组一组地抬脚，走起来。""",
        },
    }
    return (TEXT,)


if __name__ == "__main__":
    app.run()
