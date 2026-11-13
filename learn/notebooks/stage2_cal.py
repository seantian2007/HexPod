import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium", app_title="HexPod Academy · Stage 2 Calibration")


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
    _names = ["θ → us", "frame", "check", "clock"]
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
def _():
    # ── Given — you don't need to change anything here ──
    K = 0.0901                                     # degrees per µs (Stage 0), the same for every servo
    LEGS = ["R1", "R2", "R3", "L1", "L2", "L3"]
    JOINTS = ["coxa", "femur", "tibia"]
    NAMES = [f"{l} {j}" for l in LEGS for j in JOINTS]            # joint i = 3 * leg + type
    REF = [0, 0, 90]                                # reference angle per joint type: coxa, femur, tibia
    LIMITS = [(-45, 45), (-75, 75), (15, 165)]      # allowed angle per joint type (degrees)
    TABLE = [                                       # (us0, s) for every joint: our robot's calibration
        (1480, 1), (1580, 1), (1550, 1),   (1520, 1), (1490, 1), (1520, 1),   (1410, 1), (1480, 1), (1530, 1),     # R1 R2 R3
        (1450, 1), (1580, -1), (1510, -1), (1490, 1), (1470, -1), (1470, -1), (1540, 1), (1500, -1), (1500, -1)]  # L1 L2 L3
    HOME = [0, 30, 105] * 6
    return HOME, K, LIMITS, NAMES, REF, TABLE


@app.cell(hide_code=True)
def _(mo, t):
    mo.vstack([mo.md(t("ex1_md")), mo.accordion({t("hint") + " 1": mo.md(t("ex1_h1")), t("hint") + " 2": mo.md(t("ex1_h2")), t("answer"): mo.md(t("ex1_a"))})])
    return


@app.cell
def _(K, REF):
    def angle_to_pulse(theta, joint, table):
        """Angle (degrees) for joint number `joint` (0-17) -> pulse width in µs, using that joint's row of `table`."""
        # ✏️ YOUR CODE HERE
        return None
    return (angle_to_pulse,)


@app.cell(hide_code=True)
def _(NAMES, TABLE, angle_to_pulse, check):
    ok1, _view = check(angle_to_pulse, [((a, j, TABLE), e, f"θ = {a}°, joint {j} ({NAMES[j]})") for a, j, e in [
        (10, 9, 1560.9878), (-20, 10, 1801.9756), (60, 11, 1842.9634), (30, 1, 1912.9634), (105, 2, 1716.4817), (90, 5, 1520.0)]], tol=0.001)
    _view
    return (ok1,)


@app.cell(hide_code=True)
def _(mo, t):
    mo.vstack([mo.md(t("ex2_md")), mo.accordion({t("hint") + " 1": mo.md(t("ex2_h1")), t("hint") + " 2": mo.md(t("ex2_h2")), t("answer"): mo.md(t("ex2_a"))})])
    return


@app.cell
def _(LIMITS, angle_to_pulse):
    def frame_pulses(angles, table):
        """18 angles (R1..L3 × coxa, femur, tibia) -> list of 18 whole-µs pulses, or None if any angle is outside LIMITS."""
        # ✏️ YOUR CODE HERE
        return None
    return (frame_pulses,)


@app.cell(hide_code=True)
def _(HOME, TABLE, check, frame_pulses):
    _bad = list(HOME)
    _bad[13] = 80
    ok2, _view = check(frame_pulses, [
        ((HOME, TABLE), [1480, 1913, 1716, 1520, 1823, 1686, 1410, 1813, 1696, 1450, 1247, 1344, 1490, 1137, 1304, 1540, 1167, 1334], "home (0, 30, 105) × 6"),
        (([0, 0, 90] * 6, TABLE), [u for u, _ in TABLE], "reference (0, 0, 90) × 6"),
        ((_bad, TABLE), None, "home, but L2 femur = 80°")], tol=0)
    _view
    return (ok2,)


@app.cell(hide_code=True)
def _(mo, t):
    mo.vstack([mo.md(t("ex3_md")), mo.accordion({t("hint") + " 1": mo.md(t("ex3_h1")), t("answer"): mo.md(t("ex3_a"))})])
    return


@app.cell
def _():
    def check_table(table):
        """Return the sorted list of joint numbers whose row looks wrong."""
        # ✏️ YOUR CODE HERE
        return None
    return (check_table,)


@app.cell(hide_code=True)
def _(TABLE, check, check_table, mo, t):
    def _edit(changes):
        tb = list(TABLE)
        for i, row in changes.items():
            tb[i] = row
        return tb
    ok3, _view = check(check_table, [
        ((TABLE,), [6], "our table"),
        ((_edit({4: (1600, 1)}),), [4, 6], "R2 femur us0 = 1600"),
        ((_edit({7: (1480, 0), 12: (1395, 1)}),), [6, 7, 12], "R3 femur s = 0, L2 coxa us0 = 1395"),
        ((_edit({0: (1420, -1), 6: (1570, 1)}),), [], "R1 coxa (1420, −1), R3 coxa (1570, 1)"),
        ((_edit({3: (1500, 2)}),), [3, 6], "R2 coxa s = 2")], tol=0)
    mo.vstack([_view, mo.md(t("tbl_note")) if ok3 else mo.md("")])
    return (ok3,)


@app.cell(hide_code=True)
def _(mo, t):
    mo.vstack([mo.md(t("ex4_md")), mo.accordion({t("hint") + " 1": mo.md(t("ex4_h1")), t("hint") + " 2": mo.md(t("ex4_h2")), t("answer"): mo.md(t("ex4_a"))})])
    return


@app.cell
def _(np):
    D = 122                       # the divisor the library picked, believing the clock is 25 MHz
    TICK_US = D / 25e6 * 1e6      # what it believes one tick lasts: 4.88 µs

    def real_clock(asked, measured):
        """asked, measured: pulse widths in µs. Returns the board's real clock in MHz."""
        asked, measured = np.asarray(asked, dtype=float), np.asarray(measured, dtype=float)
        # ✏️ YOUR CODE HERE
        return None
    return (real_clock,)


@app.cell(hide_code=True)
def _(check, mo, real_clock, t):
    ok4, _view = check(real_clock, [(([1000, 1500, 2000], [967, 1452, 1939]), 25.8184, "left board"),
                                    (([1000, 1500, 2000], [957, 1442, 1917]), 26.0668, "right board"),
                                    (([1000, 2000], [1000, 2000]), 25.01, "a perfect 25 MHz board?")], tol=0.001)
    mo.vstack([_view, mo.md(t("clock_after")) if ok4 else mo.md("")])
    return (ok4,)


@app.cell(hide_code=True)
def _(mo, t):
    which = mo.ui.radio(options={t("tb_none"): "none", t("tb_us0"): "us0", t("tb_full"): "full"}, value=t("tb_none"), label=t("tb_pick"))
    mo.vstack([mo.md(t("r1_md")), which])
    return (which,)


@app.cell(hide_code=True)
def _(HOME, K, NAMES, REF, TABLE, frame_pulses, mo, np, ok1, ok2, ok3, ok4, player, t, which):
    def _true_angles(pulses):
        """What our real servos do with these pulses (the hidden truth is TABLE)."""
        return [s * K * (p - u) + REF[i % 3] for i, (p, (u, s)) in enumerate(zip(pulses, TABLE))]

    def _foot_z(a):
        t2, t23 = np.radians(a[1]), np.radians(a[1] - a[2])
        return 76 * np.sin(t2) + 132 * np.sin(t23)

    if not (ok1 and ok2 and ok3 and ok4):
        _out = mo.callout(mo.md("🔒 " + t("r_locked")), kind="neutral")
    else:
        _tb = {"none": [(1500, 1)] * 18, "us0": [(u, 1) for u, _ in TABLE], "full": TABLE}[which.value]
        _p = frame_pulses(HOME, _tb)
        if _p is None:
            _out = mo.callout(mo.md(t("r1_none")), kind="danger")
        else:
            _a = np.array(_true_angles(_p)).reshape(6, 3)
            _err = np.abs(_a - np.reshape(HOME, (6, 3)))
            _z = np.array([_foot_z(a) for a in _a])
            _gap = _z - _z.min()
            _worst = int(np.argmax(_err.max(axis=1)))
            _rows = "\n".join(f"| {NAMES[3 * i][:2]} | {_a[i, 0]:.1f}° | {_a[i, 1]:.1f}° | {_a[i, 2]:.1f}° | {_gap[i]:.1f} mm |" for i in range(6))
            _cfg = {"mode": "hex", "angles": [[[round(float(v), 2) for v in a] for a in _a]], "fps": 1,
                    "labels": [t("r1_lbl").format(e=_err.max())]}
            _kind = "success" if _err.max() < 0.5 else "warn"
            _out = mo.vstack([player(_cfg, 360), mo.md(t("r1_th") + "\n|---|---|---|---|---|\n" + _rows),
                              mo.callout(mo.md(t("r1_ok") if _err.max() < 0.5 else t("r1_bad").format(e=_err.max(), leg=NAMES[3 * _worst][:2])), kind=_kind)])
    _out
    return


@app.cell(hide_code=True)
def _(IN_BROWSER, mo, t):
    robot_on = mo.ui.switch(label=t("robot_switch"))
    send = mo.ui.run_button(label=t("robot_send"))
    mo.vstack([mo.md(t("robot_md")),
               mo.callout(mo.md(t("robot_browser")), kind="neutral") if IN_BROWSER else mo.hstack([robot_on, send], justify="start")])
    return robot_on, send


@app.cell(hide_code=True)
def _(HOME, IN_BROWSER, mo, np, robot_on, send, t):
    mo.stop(IN_BROWSER or not send.value)
    mo.stop(not robot_on.value, mo.callout(mo.md(t("robot_need_switch")), kind="warn"))

    import pathlib, sys as _sys
    _code_dir = pathlib.Path(mo.notebook_dir()).resolve().parents[1]           # .../code
    if str(_code_dir) not in _sys.path:
        _sys.path.insert(0, str(_code_dir))
    from utils.link import Link

    _link = Link()
    try:
        _link.move_to(np.array(HOME, dtype=float), 2)
    finally:
        _link.close()
    mo.callout(mo.md(t("robot_done")), kind="success")
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
            "crumb": 'Stage 2 · Calibration · practice',
            "intro": """# Make the servos agree with the math 📏
    
    The math from Stage 1 speaks in **angles**; the servos only understand **pulses**. Calibration is the table that translates one into the other, joint by joint. You'll write **4 small pieces**: one joint's conversion, a whole frame of 18 pulses, a sanity check for the table, and the clock correction.
    
    How to work: edit the code cells marked ✏️, then run them (Ctrl/Cmd + Enter). The checker under each one updates on its own. If you're stuck, open the hints one at a time; the last one is the full answer. Pass all four to unlock a **crooked robot** that straightens out when you give it the right table.""",
            "given_md": """## What you're given
    
    - **Joint numbers.** The robot has 18 joints, numbered 0 to 17: three per leg in the order coxa, femur, tibia, and the legs in the order R1, R2, R3, L1, L2, L3. So joint i belongs to leg i // 3 (whole-number division), and its **type** is i % 3 (the remainder: 0 = coxa, 1 = femur, 2 = tibia). `NAMES[i]` spells it out.
    - **K = 0.0901 °/µs**, from Stage 0: degrees per µs, the same for all servos.
    - **TABLE**: one row (us0, s) per joint, our robot's real calibration.
      - **us0** (µs): the pulse at which that joint sits at its **reference angle**, the pose we line it up against: coxa 0°, femur 0°, tibia **90°** (`REF`).
      - **s**: the direction sign, +1 if a longer pulse turns the joint the positive way, −1 if the other way. Mirrored left legs have some servos mounted the other way round.
    - **LIMITS**: the allowed angle range per joint type. **HOME**: the standing pose, (0°, 30°, 105°) on every leg.""",
            "ex1_md": """## ✏️ 1 · One joint: angle → pulse
    
    The page's formula, written for a joint whose zero is its reference angle:
    
    **us = us0 + s · (θ − ref) / K**
    
    - θ − ref is how far you want the joint from the pose where it was calibrated. For coxa and femur ref = 0, so it's just θ. For the tibia ref = 90°, because we calibrated it at a right angle.
    - Dividing by K turns degrees into µs (about 11.1 µs per degree). Multiplying by s flips the direction for mirrored joints.
    
    Write `angle_to_pulse(theta, joint, table)`: look up the row for `joint` in `table`, find its reference angle from its type, and return the pulse (a float; we round later).""",
            "ex1_h1": '`us0, s = table[joint]` unpacks the row. The type is `joint % 3`, so the reference is `REF[joint % 3]`.',
            "ex1_h2": "Check by hand: R1 tibia (joint 2) at 105°: 1550 + (105 − 90) / 0.0901 = 1550 + 166.5 = 1716.5 µs. Forgetting the − 90 would give 2715 µs, past the servo's end.",
            "ex1_a": """```python
    us0, s = table[joint]
    ref = REF[joint % 3]
    return us0 + s * (theta - ref) / K
    ```""",
            "ex2_md": """## ✏️ 2 · A whole frame
    
    Every 20 ms the robot needs one **frame**: all 18 pulses at once, as whole microseconds (our firmware reads integers). Before turning anything into a pulse, refuse what the robot must never do: if **any** angle is outside the LIMITS for its joint type, return `None` and send nothing.
    
    Write `frame_pulses(angles, table)` that returns a list of 18 whole numbers, or None. The checker uses two poses whose answers you can predict:
    - **home**: the pulses our robot really stands on;
    - **the reference pose (0°, 0°, 90°) on every leg**: θ − ref is 0 for every joint, so the answer must be exactly the table's us0 column.""",
            "ex2_h1": 'Loop with `for i, a in enumerate(angles):`. The limits for joint i are `LIMITS[i % 3]`. Return None as soon as one angle is out of range.',
            "ex2_h2": 'Otherwise append `round(angle_to_pulse(a, i, table))`. `round()` gives the nearest whole number.',
            "ex2_a": """```python
    out = []
    for i, a in enumerate(angles):
        lo, hi = LIMITS[i % 3]
        if not lo <= a <= hi:
            return None
        out.append(round(angle_to_pulse(a, i, table)))
    return out
    ```""",
            "ex3_md": """## ✏️ 3 · Sanity-check the table
    
    A typo in the table can slam a leg into the body, so check it before using it. Two rules from the page:
    
    - **The horn's tooth.** The output shaft has 25 teeth, so the horn can be pushed on in steps of 360° / 25 = 14.4°, which is 14.4 / 0.0901 ≈ 160 µs. If you picked the best tooth, the joint's reference pose is at most half a tooth from the middle pulse, 1500 µs: **|us0 − 1500| ≤ 80 µs**. More than that means the horn sits on the wrong tooth (or the number is a typo).
    - **The sign.** s must be exactly **+1 or −1**.
    
    Write `check_table(table)` that returns the sorted list of joint numbers that break either rule (an empty list if the table is fine).""",
            "ex3_h1": 'Loop over `enumerate(table)`; for each row `(us0, s)` flag it if `abs(us0 - 1500) > 80` or `s not in (1, -1)`. Looping in order already gives a sorted list.',
            "ex3_a": """```python
    bad = []
    for i, (us0, s) in enumerate(table):
        if abs(us0 - 1500) > 80 or s not in (1, -1):
            bad.append(i)
    return bad
    ```""",
            "tbl_note": "Look at the first test: your check flags a row of **our own** table, joint 6 (R3 coxa, us0 = 1410, 90 µs from 1500). The rule is doing its job. Re-seating that horn one tooth (≈ 160 µs) would move us0 to about 1570, only 70 µs from 1500. It's 10 µs (≈ 1°) past the line, so the robot works as it is, but it's worth fixing the next time that leg is off.",
            "ex4_md": """## ✏️ 4 · Find each board's real clock
    
    Stage 0 showed that the PCA9685's clock is not exactly 25 MHz. Here is how we measured it, one step at a time:
    
    1. The library **believes** the clock is 25 MHz. So it picked the divisor **D = 122** and believes one tick lasts **TICK_US = 122 / 25 MHz = 4.88 µs**.
    2. Asked for a pulse of `asked` µs, it sends **n = round(asked / TICK_US)** whole ticks. That part is pure arithmetic, so we know n exactly.
    3. On the chip, n ticks really take n · D clock beats. At the real clock f (in beats per µs, which is the same number as MHz), that lasts **measured = n · D / f** µs. We timed `measured` with the Arduino Nano.
    4. Solve for f: **f = n · D / measured**. Three measurements give three estimates; average them.
    
    Write `real_clock(asked, measured)` that returns f in MHz. Both inputs are arrays of the same length.""",
            "ex4_h1": '`n = np.round(asked / TICK_US)` works on the whole array at once. Then `n * D / measured` is an array of three estimates.',
            "ex4_h2": 'Return `float(np.mean(...))`. For the left board you should get about 25.82.',
            "ex4_a": """```python
    n = np.round(asked / TICK_US)           # ticks the chip really sent
    return float(np.mean(n * D / measured))  # beats per µs = MHz
    ```""",
            "clock_after": 'Our firmware uses **25.8 MHz** (left) and **26.0 MHz** (right). Your numbers: 25.82 and 26.07. The right board is 0.07 MHz off, 0.3%: about 4 µs at 1500 µs, under the servo\'s 8 µs deadband, so it doesn\'t matter. Why the slight spread between the three estimates? Each measurement is only good to about ±1 µs, and n was rounded. That rounding is also why the "perfect" board comes out at 25.01, not 25.00: 1000 µs is 204.8 ticks, but the chip can only send 205.',
            "tb_pick": 'Which table do we send with?',
            "tb_none": 'nothing calibrated: every us0 = 1500, every s = +1',
            "tb_us0": 'us0 from the table, but every s = +1',
            "tb_full": 'the full table (us0 and s)',
            "r1_md": """## ★ Reward · Straighten the crooked robot
    
    The simulated robot below has our real servos inside: their true us0 and s are the ones in TABLE. We ask it for home, (0°, 30°, 105°) on every leg, and convert with **your** `frame_pulses` using the table you pick. The robot then does what real servos do with those pulses. The table lists the angles each leg really ends up at, and how far each foot hangs above the lowest one. Drag to rotate.""",
            "r1_lbl": 'worst joint error {e:.1f}°',
            "r1_th": '| leg | θ1 | θ2 | θ3 | foot above lowest |',
            "r1_none": 'frame_pulses() refused this frame: some pulse would put a joint past its limit.',
            "r1_bad": 'Worst joint is off by **{e:.1f}°** (leg {leg}), and some feet hang far above the others. Even a foot just a few mm too high carries no weight. Try the next table.',
            "r1_ok": '**Every joint is exactly where the math says, and all six feet are level.** This is what the paper test checks on the real robot.',
            "robot_md": """## 🤖 Bonus · The paper test
    
    Stand the real robot on a table at home through `utils/link.py` (it uses the table in `constants.py`, so make sure that one matches yours). Then slide a strip of paper under each foot. Every foot should pin its paper. If one slides out, lower that foot by changing its femur us0 by about 10 µs (≈ 0.9°, ≈ 1.6 mm of foot height) and test again. **Keep the USB cable slack.**""",
            "robot_send": '▶ Stand up at home',
            "robot_done": 'The robot is at home. Now do the paper test under all six feet.',
            "outro": """## What you just learned
    - Calibration is a table: one **us0** and one **s** per joint, plus one **K** for all of them. The tibia's us0 belongs to **90°**, so subtract the reference angle first.
    - Check the table before using it: **|us0 − 1500| ≤ 80 µs** (half a tooth) and **s = ±1**.
    - Refuse a whole frame if any angle is out of range: sending nothing is always safe.
    - A wrong clock is a **proportional** error. Fix it (one number per board) before you calibrate.
    
    **Next: Stage 3 · Inverse kinematics.** Point at a spot; find the three angles.""",
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
            "crumb": '阶段 2 · 标定 · 练习',
            "intro": """# 让舵机和数学一致 📏
    
    阶段 1 的数学说的是**角度**；舵机只懂**脉宽**。标定就是一张把前者翻译成后者的表，一个关节一行。你会写 **4 小块**：单个关节的换算、一整帧 18 个脉宽、表格的合理性检查，以及时钟修正。
    
    怎么做：修改标了 ✏️ 的代码格子，然后运行（Ctrl/Cmd + Enter）。每个格子下面的检查器会自动更新。卡住了就一条一条展开提示，最后一条是完整答案。四个全部通过后，解锁一个**歪歪扭扭的机器人**：给它正确的表，它就站直了。""",
            "given_md": """## 已经给你的东西
    
    - **关节编号。** 机器人有 18 个关节，编号 0 到 17：每条腿三个，顺序是 coxa、femur、tibia；腿的顺序是 R1、R2、R3、L1、L2、L3。所以关节 i 属于第 i // 3 条腿（整除），它的**类型**是 i % 3（余数：0 = coxa，1 = femur，2 = tibia）。`NAMES[i]` 写出它的名字。
    - **K = 0.0901 °/µs**，来自阶段 0：每 µs 对应的度数，所有舵机都一样。
    - **TABLE**：每个关节一行 (us0, s)，是我们机器人真实的标定值。
      - **us0**（µs）：让这个关节处于**参考角**的脉宽，参考角就是我们对齐时用的姿态：coxa 0°，femur 0°，tibia **90°**（`REF`）。
      - **s**：方向符号，脉宽变长时关节往正方向转为 +1，往反方向转为 −1。镜像的左腿有些舵机是反着装的。
    - **LIMITS**：每种关节允许的角度范围。**HOME**：站立姿态，每条腿 (0°, 30°, 105°)。""",
            "ex1_md": """## ✏️ 1 · 单个关节：角度 → 脉宽
    
    页面上的公式，写成以参考角为零点的形式：
    
    **us = us0 + s · (θ − ref) / K**
    
    - θ − ref 是你希望关节离标定姿态有多远。coxa 和 femur 的 ref = 0，所以就是 θ。tibia 的 ref = 90°，因为我们是在直角处标定它的。
    - 除以 K 把度数换成 µs（约每度 11.1 µs）。乘以 s 让镜像关节反向。
    
    写 `angle_to_pulse(theta, joint, table)`：在 `table` 里找到 `joint` 那一行，由关节类型找到参考角，返回脉宽（浮点数；取整留到后面）。""",
            "ex1_h1": '`us0, s = table[joint]` 把这一行拆开。类型是 `joint % 3`，所以参考角是 `REF[joint % 3]`。',
            "ex1_h2": '手算验证：R1 tibia（关节 2）在 105°：1550 + (105 − 90) / 0.0901 = 1550 + 166.5 = 1716.5 µs。忘了减 90 会得到 2715 µs，超出舵机的行程。',
            "ex1_a": """```python
    us0, s = table[joint]
    ref = REF[joint % 3]
    return us0 + s * (theta - ref) / K
    ```""",
            "ex2_md": """## ✏️ 2 · 一整帧
    
    机器人每 20 ms 需要一**帧**：18 个脉宽一起发，都是整数微秒（我们的固件读整数）。在把任何角度变成脉宽之前，先拒绝机器人绝对不能做的事：只要有**任何一个**角度超出该关节类型的 LIMITS，就返回 `None`，什么都不发。
    
    写 `frame_pulses(angles, table)`，返回 18 个整数组成的 list，或者 None。检查器用两个你能预先算出答案的姿态：
    - **home**：我们的机器人真实站立时用的脉宽；
    - **每条腿都是参考姿态 (0°, 0°, 90°)**：每个关节的 θ − ref 都是 0，所以答案必须正好等于表里的 us0 那一列。""",
            "ex2_h1": '用 `for i, a in enumerate(angles):` 循环。关节 i 的范围是 `LIMITS[i % 3]`。一旦有角度越界就立刻返回 None。',
            "ex2_h2": '否则 append `round(angle_to_pulse(a, i, table))`。`round()` 取最接近的整数。',
            "ex2_a": """```python
    out = []
    for i, a in enumerate(angles):
        lo, hi = LIMITS[i % 3]
        if not lo <= a <= hi:
            return None
        out.append(round(angle_to_pulse(a, i, table)))
    return out
    ```""",
            "ex3_md": """## ✏️ 3 · 检查表格是否合理
    
    表里一个笔误就可能让腿撞上机身，所以用之前先检查。页面上的两条规则：
    
    - **舵盘的齿。** 输出轴有 25 个齿，所以舵盘只能以 360° / 25 = 14.4° 为一步装上去，即 14.4 / 0.0901 ≈ 160 µs。如果选的是最好的那个齿，关节的参考姿态离中间脉宽 1500 µs 最多半个齿：**|us0 − 1500| ≤ 80 µs**。超过就说明舵盘装错了齿（或者是数字打错了）。
    - **符号。** s 必须正好是 **+1 或 −1**。
    
    写 `check_table(table)`，返回违反任一条规则的关节编号，排好序（表格没问题时返回空 list）。""",
            "ex3_h1": '遍历 `enumerate(table)`；对每一行 `(us0, s)`，如果 `abs(us0 - 1500) > 80` 或 `s not in (1, -1)` 就标记。按顺序遍历得到的 list 自然是排好序的。',
            "ex3_a": """```python
    bad = []
    for i, (us0, s) in enumerate(table):
        if abs(us0 - 1500) > 80 or s not in (1, -1):
            bad.append(i)
    return bad
    ```""",
            "tbl_note": '看第一个测试：你的检查标记了**我们自己**表里的一行，关节 6（R3 coxa，us0 = 1410，离 1500 有 90 µs）。规则起作用了。把这个舵盘挪一个齿（≈ 160 µs），us0 会变成约 1570，离 1500 只有 70 µs。它只超出 10 µs（≈ 1°），所以机器人现在照样能用，但下次拆这条腿时值得改过来。',
            "ex4_md": """## ✏️ 4 · 求出每块板子的真实时钟
    
    阶段 0 说过 PCA9685 的时钟不正好是 25 MHz。下面一步一步说明我们是怎么测出来的：
    
    1. 库**以为**时钟是 25 MHz。所以它选了分频数 **D = 122**，并以为一个 tick 持续 **TICK_US = 122 / 25 MHz = 4.88 µs**。
    2. 要一个 `asked` µs 的脉冲时，它发 **n = round(asked / TICK_US)** 个整 tick。这一步是纯算术，所以 n 我们是确切知道的。
    3. 在芯片上，n 个 tick 实际是 n · D 个时钟节拍。真实时钟为 f（单位：每 µs 的节拍数，数值上就等于 MHz）时，它持续 **measured = n · D / f** µs。`measured` 是我们用 Arduino Nano 计时测出来的。
    4. 解出 f：**f = n · D / measured**。三次测量给出三个估计值，取平均。
    
    写 `real_clock(asked, measured)`，返回以 MHz 为单位的 f。两个输入是长度相同的数组。""",
            "ex4_h1": '`n = np.round(asked / TICK_US)` 一次处理整个数组。然后 `n * D / measured` 就是三个估计值组成的数组。',
            "ex4_h2": '返回 `float(np.mean(...))`。左板你应该得到约 25.82。',
            "ex4_a": """```python
    n = np.round(asked / TICK_US)           # ticks the chip really sent
    return float(np.mean(n * D / measured))  # beats per µs = MHz
    ```""",
            "clock_after": '我们的固件用的是 **25.8 MHz**（左）和 **26.0 MHz**（右）。你算出的是 25.82 和 26.07。右板差 0.07 MHz，即 0.3%：在 1500 µs 时约 4 µs，小于舵机 8 µs 的死区，所以没关系。为什么三个估计值之间略有出入？每次测量只精确到约 ±1 µs，而且 n 经过了取整。取整也是那块"完美"板子算出 25.01 而不是 25.00 的原因：1000 µs 是 204.8 个 tick，但芯片只能发 205 个。',
            "tb_pick": '发送时用哪张表？',
            "tb_none": '完全没标定：所有 us0 = 1500，所有 s = +1',
            "tb_us0": '用表里的 us0，但所有 s = +1',
            "tb_full": '完整的表（us0 和 s）',
            "r1_md": """## ★ 奖励 · 把歪机器人扶正
    
    下面的模拟机器人里装的是我们真实的舵机：它们真实的 us0 和 s 就是 TABLE 里的值。我们让它站到 home，每条腿 (0°, 30°, 105°)，用**你的** `frame_pulses` 和你选的那张表换算成脉宽。然后机器人就像真舵机那样执行这些脉宽。表格列出每条腿实际到达的角度，以及每只脚比最低那只脚高出多少。拖动可以旋转。""",
            "r1_lbl": '最大关节误差 {e:.1f}°',
            "r1_th": '| 腿 | θ1 | θ2 | θ3 | 脚比最低点高出 |',
            "r1_none": 'frame_pulses() 拒绝了这一帧：有脉宽会让关节越过限位。',
            "r1_bad": '误差最大的关节差了 **{e:.1f}°**（{leg} 腿），有些脚比别的脚高出一大截。哪怕只高几毫米，那只脚也不承重。试试下一张表。',
            "r1_ok": '**每个关节都正好在数学说的位置，六只脚一样高。** 这正是真机上纸条测试要检查的。',
            "robot_md": """## 🤖 附加 · 纸条测试
    
    通过 `utils/link.py` 让真机器人在桌上站到 home（它用的是 `constants.py` 里的表，确认那张表和你的一致）。然后在每只脚下塞一张纸条。每只脚都应该压住纸条。如果某张纸条能抽出来，就把那条腿的 femur us0 改约 10 µs（≈ 0.9°，≈ 1.6 mm 脚尖高度），让那只脚低一点，再测一遍。**USB 线要留松。**""",
            "robot_send": '▶ 站到 home',
            "robot_done": '机器人已站到 home。现在对六只脚做纸条测试。',
            "outro": """## 你刚学到的
    - 标定就是一张表：每个关节一个 **us0** 和一个 **s**，所有关节共用一个 **K**。tibia 的 us0 对应 **90°**，所以要先减去参考角。
    - 用之前先检查表：**|us0 − 1500| ≤ 80 µs**（半个齿），**s = ±1**。
    - 只要有一个角度越界就拒绝整帧：什么都不发永远是安全的。
    - 时钟不对是**按比例**的误差。先修正它（每块板子一个数），再做标定。
    
    **下一步：阶段 3 · 逆运动学。** 指一个点，求出三个角。""",
        },
    }
    return (TEXT,)


if __name__ == "__main__":
    app.run()
