import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium", app_title="HexPod Academy · Stage 4 Jacobian")


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
    _names = ["J", "det, κ", "τ = JᵀF", "map"]
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
    STALL = 25.0          # servo stall torque, kg·cm
    KGCM = 98.0665        # N·mm in one kg·cm (9.80665 N × 10 mm)

    def fk(theta1, theta2, theta3):
        """Joint angles (deg) -> foot (x, y, z) in mm, leg frame."""
        t1, t2, t23 = np.radians(theta1), np.radians(theta2), np.radians(theta2 - theta3)
        r = L1 + L2 * np.cos(t2) + L3 * np.cos(t23)
        z = L2 * np.sin(t2) + L3 * np.sin(t23)
        return np.array([r * np.cos(t1), r * np.sin(t1), z])

    def ik(x, y, z):
        """Foot (mm, leg frame) -> angles (deg), knee up, or None if out of reach / past a limit."""
        t1 = np.degrees(np.arctan2(y, x))
        u = np.hypot(x, y) - L1
        c = (u * u + z * z - L2 * L2 - L3 * L3) / (2 * L2 * L3)
        if abs(c) > 1:
            return None
        t3 = np.arccos(c)
        t2 = np.degrees(np.arctan2(z, u) + np.arctan2(L3 * np.sin(t3), L2 + L3 * np.cos(t3)))
        a = np.array([t1, t2, np.degrees(t3)])
        if abs(a[0]) > 45 or abs(a[1]) > 75 or not 15 <= a[2] <= 165:
            return None
        return a

    HOME = (0, 30, 105)
    return HOME, KGCM, L1, L2, L3, STALL, fk, ik


@app.cell(hide_code=True)
def _(mo, t):
    mo.vstack([mo.md(t("ex1_md")), mo.accordion({t("hint") + " 1": mo.md(t("ex1_h1")), t("hint") + " 2": mo.md(t("ex1_h2")), t("answer"): mo.md(t("ex1_a"))})])
    return


@app.cell
def _(L1, L2, L3, np):
    def jacobian(theta1, theta2, theta3):
        """3×3 Jacobian in mm per radian: row = x, y, z of the foot; column = joint 1, 2, 3."""
        # ✏️ YOUR CODE HERE
        return None
    return (jacobian,)


@app.cell(hide_code=True)
def _(fk, jacobian, mo, np, t, verdict):
    def _fd(a, h=1e-6):
        """Finite differences: nudge one joint by ±h rad and watch the foot."""
        out = np.zeros((3, 3))
        for j in range(3):
            d = np.zeros(3)
            d[j] = np.degrees(h)
            out[:, j] = (fk(*(np.add(a, d))) - fk(*(np.subtract(a, d)))) / (2 * h)
        return out

    def _run():
        _rng = np.random.default_rng(4)
        _poses = [(0, 30, 105)] + [(_rng.uniform(-45, 45), _rng.uniform(-75, 75), _rng.uniform(15, 165)) for _ in range(30)]
        _worst, _at = 0.0, None
        for a in _poses:
            try:
                J = jacobian(*a)
            except Exception as e:
                return False, verdict(False, [f"❌ error: {type(e).__name__}: {e}"])
            if J is None:
                return False, mo.callout(mo.md("✏️ " + t("not_started")), kind="neutral")
            J = np.asarray(J, dtype=float)
            if J.shape != (3, 3):
                return False, verdict(False, ["❌ " + t("shape").format(s=J.shape)])
            e = float(np.max(np.abs(J - _fd(a))))
            if e > _worst:
                _worst, _at = e, a
        _ok = _worst < 1e-4
        _home = np.asarray(jacobian(0, 30, 105), dtype=float)
        _lines = [("✅ " if _ok else "❌ ") + t("fd_res").format(n=len(_poses), w=_worst),
                  t("fd_home") + "\n\n```\n" + np.array2string(_home, precision=1, suppress_small=True) + "\n```"]
        if not _ok:
            _lines.append(t("fd_where").format(a=np.round(_at, 1).tolist()) + "\n\n```\n" + np.array2string(_fd(_at), precision=1, suppress_small=True) + "\n```")
        return _ok, verdict(_ok, _lines)

    ok1, _view = _run()
    _view
    return (ok1,)


@app.cell(hide_code=True)
def _(mo, t):
    mo.vstack([mo.md(t("ex2_md")), mo.accordion({t("hint") + " 1": mo.md(t("ex2_h1")), t("hint") + " 2": mo.md(t("ex2_h2")), t("answer"): mo.md(t("ex2_a"))})])
    return


@app.cell
def _(L1, L2, L3, np):
    def det_formula(theta1, theta2, theta3):
        """det J from the page's formula: −r · L2 · L3 · sin θ3."""
        # ✏️ YOUR CODE HERE
        return None

    def kappa(M):
        """Condition number of any matrix M: largest singular value / smallest."""
        # ✏️ YOUR CODE HERE
        return None
    return det_formula, kappa


@app.cell(hide_code=True)
def _(check, det_formula, jacobian, kappa, mo, np, ok1, t):
    _rng = np.random.default_rng(5)
    _poses = [(0, 30, 105), (20, -10, 60)] + [tuple(np.round([_rng.uniform(-45, 45), _rng.uniform(-75, 75), _rng.uniform(15, 165)], 1)) for _ in range(4)]
    if ok1:
        _okD, _vD = check(det_formula, [(p, float(np.linalg.det(jacobian(*p)))) for p in _poses], tol=0.5)
    else:
        _okD, _vD = False, mo.callout(mo.md(t("ex2_wait")), kind="neutral")
    _Jh = np.array([[0, 89.5022, -127.5022], [161.982, 0, 0], [0, 99.982, -34.1641]])
    _okK, _vK = check(kappa, [((np.eye(3),), 1.0, "identity"), ((np.diag([2.0, 1.0]),), 2.0, "diag(2, 1)"),
                              ((_Jh[[0, 2]][:, [1, 2]],), 3.3587, "home, side view (rows x, z; columns 2, 3)"),
                              ((_Jh,), 3.3586, "home, full 3×3")], tol=0.001)
    ok2 = _okD and _okK
    mo.vstack([mo.md("`det_formula` " + t("vs_det")), _vD, mo.md("`kappa`"), _vK, mo.md(t("ex2_after")) if ok2 else mo.md("")])
    return (ok2,)


@app.cell(hide_code=True)
def _(mo, t):
    mo.vstack([mo.md(t("ex3_md")), mo.accordion({t("hint") + " 1": mo.md(t("ex3_h1")), t("hint") + " 2": mo.md(t("ex3_h2")), t("answer"): mo.md(t("ex3_a"))})])
    return


@app.cell
def _(KGCM, jacobian, np):
    def torques(theta, F):
        """theta = (θ1, θ2, θ3) in degrees, F = force the foot pushes on the ground (N).
        Returns the three joint torques in kg·cm."""
        # ✏️ YOUR CODE HERE
        return None
    return (torques,)


@app.cell(hide_code=True)
def _(check, mo, t, torques):
    ok3, _view = check(torques, [(((0, 30, 105), (0, 0, -7.2)), (0.0, -7.3406, 2.5083), "home, tripod load"),
                                 (((0, 30, 105), (0, 0, -3.6)), (0.0, -3.6703, 1.2542), "home, all six feet down"),
                                 (((20, -10, 60), (1, 2, -7.2)), (2.8530, -6.5375, 1.2609))], tol=0.001)
    mo.vstack([_view, mo.md(t("ex3_after")) if ok3 else mo.md("")])
    return (ok3,)


@app.cell(hide_code=True)
def _(mo, t):
    mo.vstack([mo.md(t("ex4_md")), mo.accordion({t("hint") + " 1": mo.md(t("ex4_h1")), t("hint") + " 2": mo.md(t("ex4_h2")), t("answer"): mo.md(t("ex4_a"))})])
    return


@app.cell
def _(L1, STALL, ik, jacobian, kappa, np, torques):
    def stance_map(us, zs, load=7.2):
        """For every foot position (u, z) in the side view (θ1 = 0), with the foot pressing down with `load` N:
        returns (tau2_pct, kap), two arrays of shape (len(zs), len(us)). Use np.nan where ik() has no answer."""
        tau2_pct = np.full((len(zs), len(us)), np.nan)
        kap = np.full((len(zs), len(us)), np.nan)
        for i, z in enumerate(zs):
            for j, u in enumerate(us):
                # ✏️ YOUR CODE HERE
                pass
        return tau2_pct, kap
    return (stance_map,)


@app.cell(hide_code=True)
def _(mo, np, stance_map, t, verdict):
    def _check4():
        _us, _zs = [60, 100, 140, 200], [-130, -89.5, -40]
        _T = np.array([[17.6207, 29.3678, 41.115, np.nan], [17.6207, 29.3678, 41.115, np.nan], [np.nan, 29.3678, 41.115, 58.7357]])
        _K = np.array([[3.5319, 4.2607, 7.037, np.nan], [3.2365, 3.3588, 4.3729, np.nan], [np.nan, 3.2369, 3.5909, 14.6874]])
        try:
            _t, _k = stance_map(_us, _zs)
        except Exception as e:
            return False, verdict(False, [f"❌ error: {type(e).__name__}: {e}"])
        _t, _k = np.asarray(_t, dtype=float), np.asarray(_k, dtype=float)
        if np.all(np.isnan(_t)):
            return False, mo.callout(mo.md("✏️ " + t("not_started")), kind="neutral")
        _same = lambda a, b: a.shape == b.shape and bool(np.all((np.isnan(a) & np.isnan(b)) | (np.abs(a - b) < 0.01)))
        _ok = _same(_t, _T) and _same(_k, _K)
        _fmt = lambda a: "\n".join("  ".join("   —  " if np.isnan(v) else f"{v:6.2f}" for v in row) for row in a)
        return _ok, verdict(_ok, [("✅ " if _ok else "❌ ") + t("map_res"),
                                  t("map_tau") + "\n```\n" + _fmt(_t) + "\n```", t("map_k") + "\n```\n" + _fmt(_k) + "\n```"])

    ok4, _view = _check4()
    _view
    return (ok4,)


@app.cell(hide_code=True)
def _(mo, t):
    pick_u = mo.ui.slider(40, 180, value=100, step=5, label="u (mm)", show_value=True)
    pick_z = mo.ui.slider(-160, -30, value=-90, step=5, label="z (mm)", show_value=True)
    why = mo.ui.text_area(placeholder=t("why_ph"), label=t("why_label"), full_width=True)
    mo.vstack([mo.md(t("r1_md")), mo.hstack([pick_u, pick_z], wrap=True), why])
    return pick_u, pick_z, why


@app.cell(hide_code=True)
def _(L1, STALL, ik, mo, np, ok1, ok2, ok3, ok4, pick_u, pick_z, player, stance_map, t, torques):
    def _heat(A, us, zs, vmax, title, mark):
        W, H, l, b = 300, 250, 34, 26
        cw, ch = (W - l - 6) / len(us), (H - b - 18) / len(zs)
        out = [f"<svg viewBox='0 0 {W} {H}' style='width:100%;max-width:320px;font:10px monospace'><text x='{l}' y='11' fill='currentColor'>{title}</text>"]
        for i in range(len(zs)):
            for j in range(len(us)):
                v = A[len(zs) - 1 - i, j]
                if np.isnan(v):
                    continue
                h = min(1.0, v / vmax)
                out.append(f"<rect x='{l + j * cw:.1f}' y='{16 + i * ch:.1f}' width='{cw + 0.6:.1f}' height='{ch + 0.6:.1f}' fill='hsl({200 - 175 * h:.0f},70%,{60 - 12 * h:.0f}%)'/>")
        mx = l + (mark[0] - us[0]) / (us[-1] - us[0]) * (W - l - 6 - cw) + cw / 2
        my = 16 + (zs[-1] - mark[1]) / (zs[-1] - zs[0]) * (H - b - 18 - ch) + ch / 2
        out.append(f"<circle cx='{mx:.1f}' cy='{my:.1f}' r='6' fill='none' stroke='currentColor' stroke-width='2.5'/>")
        out.append(f"<text x='{l}' y='{H - 8}' fill='currentColor'>u {us[0]:.0f}…{us[-1]:.0f}</text><text x='{W - 6}' y='{H - 8}' text-anchor='end' fill='currentColor'>z {zs[0]:.0f}…{zs[-1]:.0f}</text></svg>")
        return mo.Html("".join(out))

    def _bars(vals, labels, cap=100):
        W, rowh = 300, 22
        out = [f"<svg viewBox='0 0 {W} {rowh * len(vals) + 8}' style='width:100%;max-width:320px;font:11px monospace'>"]
        for k, (v, lb) in enumerate(zip(vals, labels)):
            w = max(1, min(1, abs(v) / cap) * (W - 120))
            out.append(f"<text x='0' y='{k * rowh + 15}' fill='currentColor'>{lb}</text><rect x='70' y='{k * rowh + 4}' width='{w:.1f}' height='14' rx='3' fill='{'#d9771f' if abs(v) > 50 else '#2a6fb0'}'/>"
                       f"<text x='{74 + w:.1f}' y='{k * rowh + 15}' fill='currentColor'>{abs(v):.0f}%</text>")
        return mo.Html("".join(out) + "</svg>")

    if not (ok1 and ok2 and ok3 and ok4):
        _out = mo.callout(mo.md("🔒 " + t("r_locked")), kind="neutral")
    else:
        _us, _zs = np.arange(30, 201, 5.0), np.arange(-170, -19, 5.0)
        _T, _K = stance_map(_us, _zs)
        _a = ik(L1 + pick_u.value, 0, pick_z.value)
        _maps = mo.hstack([_heat(_T, _us, _zs, 100, t("map_tau_t"), (pick_u.value, pick_z.value)),
                           _heat(np.minimum(_K, 12), _us, _zs, 12, t("map_k_t"), (pick_u.value, pick_z.value))], wrap=True)
        if _a is None:
            _out = mo.vstack([_maps, mo.callout(mo.md(t("r1_none")), kind="warn")])
        else:
            _ang = [[round(float(v), 2) for v in _a]] * 6
            _tri = [torques(_a, (0, 0, -7.2))[1] / STALL * 100 if i in (0, 2, 4) else 0.0 for i in range(6)]
            _six = torques(_a, (0, 0, -3.6))[1] / STALL * 100
            _j = int(np.argmin(np.abs(_us - pick_u.value))); _i = int(np.argmin(np.abs(_zs - pick_z.value)))
            _cfg = {"mode": "hex", "angles": [_ang], "fps": 1, "labels": [f"θ = ({_a[0]:.0f}°, {_a[1]:.1f}°, {_a[2]:.1f}°)"]}
            _out = mo.vstack([_maps, mo.hstack([player(_cfg, 300), mo.vstack([mo.md(t("bars_tri")), _bars(_tri, ["R1", "R2", "R3", "L1", "L2", "L3"]),
                                                                                mo.md(t("bars_six").format(p=abs(_six)))])], widths=[3, 2], wrap=True),
                              mo.callout(mo.md(t("r1_done").format(tau=abs(_tri[0]), k=_K[_i, _j], h=-pick_z.value)), kind="success")])
    _out
    return


@app.cell(hide_code=True)
def _(IN_BROWSER, mo, t):
    stance = mo.ui.dropdown(options={t("st_low"): "low", t("st_med"): "med", t("st_wide"): "wide"}, value=t("st_med"), label=t("st_pick"))
    robot_on = mo.ui.switch(label=t("robot_switch"))
    send = mo.ui.run_button(label=t("robot_send"))
    mo.vstack([mo.md(t("robot_md")),
               mo.callout(mo.md(t("robot_browser")), kind="neutral") if IN_BROWSER else mo.hstack([stance, robot_on, send], justify="start")])
    return robot_on, send, stance


@app.cell(hide_code=True)
def _(IN_BROWSER, L1, ik, mo, np, robot_on, send, stance, t):
    mo.stop(IN_BROWSER or not send.value)
    mo.stop(not robot_on.value, mo.callout(mo.md(t("robot_need_switch")), kind="warn"))

    import pathlib, sys as _sys
    _code_dir = pathlib.Path(mo.notebook_dir()).resolve().parents[1]           # .../code
    if str(_code_dir) not in _sys.path:
        _sys.path.insert(0, str(_code_dir))
    from utils.link import Link

    _uz = {"low": (100, -60), "med": (100, -89.5), "wide": (140, -89.5)}[stance.value]
    _a = ik(L1 + _uz[0], 0, _uz[1])
    _link = Link()
    try:
        _link.move_to(np.array([0, 30, 105] * 6, dtype=float), 2)
        _link.move_to(np.tile(_a, 6), 3)
    finally:
        _link.close()
    mo.callout(mo.md(t("robot_done").format(a=np.round(_a, 1).tolist())), kind="success")
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
            const pts=HX.draw(ctx,cv.width,cv.height,{legDefs:LEG,angles:CFG.angles[k],pose:ZERO,az,el:0.55,scale:s,body:false,ox:-s*95,cy:0.78,gridR:200,
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
            "crumb": 'Stage 4 · Jacobian and statics · practice',
            "intro": """# How does a small joint move change the foot? 📐
    
    The **Jacobian** J is the table of rates that links joint motion to foot motion. With it you can answer three practical questions: how precisely can the foot be placed, where does the leg lose a direction, and how hard must each servo push. You'll build it in **4 small pieces**: J itself, its determinant and condition number, the joint torques, and a map for choosing the stance.
    
    How to work: edit the code cells marked ✏️, then run them (Ctrl/Cmd + Enter). The checker under each one updates on its own. Every formula is checked against plain **finite differences** (nudge a joint, watch the foot), so you always know whether your algebra is right. Pass all four to unlock your **stance maps** and a robot standing where you choose.""",
            "given_md": """## What you're given
    
    - `fk(θ1, θ2, θ3)`: the foot position (x, y, z) in mm, from Stage 1. In its formulas:
      - **r** = L1 + L2·cos θ2 + L3·cos(θ2 − θ3): the foot's horizontal distance from the coxa axis;
      - **u** = r − L1: the same distance measured from the **femur** joint;
      - **z** = L2·sin θ2 + L3·sin(θ2 − θ3): the foot's height (negative = below the hip).
    - `ik(x, y, z)`: the reverse, from Stage 3 (knee up), or None.
    - **STALL** = 25 kg·cm, the servo's stall torque. **KGCM** = 98.0665: one kg·cm is 9.80665 N acting 10 mm from the axis, i.e. 98.0665 N·mm.
    
    Angles in this notebook are in **degrees** when you pass them in, but every derivative is **per radian** (mm/rad). The page's radian note explains why: d(sin θ)/dθ = cos θ holds only in radians.""",
            "ex1_md": """## ✏️ 1 · Build J
    
    A **partial derivative** ∂x/∂θ2 is how fast x changes when only θ2 turns, θ1 and θ3 held still. J collects all nine:
    
    ```
          ⎡ ∂x/∂θ1  ∂x/∂θ2  ∂x/∂θ3 ⎤      row 1: how x responds to each joint
    J  =  ⎢ ∂y/∂θ1  ∂y/∂θ2  ∂y/∂θ3 ⎥      row 2: y
          ⎣ ∂z/∂θ1  ∂z/∂θ2  ∂z/∂θ3 ⎦      row 3: z
    ```
    
    **Column j** is the foot's velocity (mm per rad) when only joint j turns. Differentiate the FK formulas one at a time; the page derived all nine:
    
    ```
          ⎡ −r·sin θ1   −z·cos θ1   L3·sin(θ2−θ3)·cos θ1 ⎤
    J  =  ⎢  r·cos θ1   −z·sin θ1   L3·sin(θ2−θ3)·sin θ1 ⎥
          ⎣     0           u          −L3·cos(θ2−θ3)    ⎦
    ```
    
    Write `jacobian(θ1, θ2, θ3)` that returns this as a 3×3 numpy array. The checker compares it with **finite differences**: nudge one joint by ±10⁻⁶ rad, see how far fk() moves the foot, divide by the nudge. That is the definition of a derivative, done with numbers.""",
            "ex1_h1": 'Compute r, z and u first (with the angles in radians), then write the matrix row by row: `np.array([[...], [...], [...]])`.',
            "ex1_h2": 'Check one entry by hand: ∂z/∂θ2 = d/dθ2 (L2·sin θ2 + L3·sin(θ2 − θ3)) = L2·cos θ2 + L3·cos(θ2 − θ3) = u. At home, J ≈ [[0, 89.5, −127.5], [162, 0, 0], [0, 100, −34.2]].',
            "ex1_a": """```python
    t1, t2, t23 = np.radians(theta1), np.radians(theta2), np.radians(theta2 - theta3)
    r = L1 + L2 * np.cos(t2) + L3 * np.cos(t23)
    z = L2 * np.sin(t2) + L3 * np.sin(t23)
    u = r - L1
    return np.array([
        [-r * np.sin(t1), -z * np.cos(t1), L3 * np.sin(t23) * np.cos(t1)],
        [ r * np.cos(t1), -z * np.sin(t1), L3 * np.sin(t23) * np.sin(t1)],
        [0.0,              u,             -L3 * np.cos(t23)],
    ])
    ```""",
            "shape": 'jacobian() returned shape {s}; it should be (3, 3).',
            "fd_res": 'Your J vs finite differences on {n} poses: worst entry off by **{w:.1e} mm/rad**.',
            "fd_home": 'Your J at home (0°, 30°, 105°), mm/rad:',
            "fd_where": 'The worst pose was {a}. Finite differences there say:',
            "ex2_md": """## ✏️ 2 · Determinant and condition number
    
    Two numbers summarise how healthy J is at a pose.
    
    **The determinant det J.** Push a tiny box of joint errors (sides δθ1, δθ2, δθ3) through J and it becomes a slanted box of foot errors. det J is the factor by which its **volume** changes (with a sign for orientation). If det J = 0, the box is squashed flat: the three columns lie in one plane, some direction of foot motion is impossible, and J has no inverse. That pose is a **singularity**. For our leg the page found
    
    **det J = −r · L2 · L3 · sin θ3**
    
    so it is zero when r = 0 (foot under the coxa axis) or sin θ3 = 0 (knee straight).
    
    **The condition number κ** (kappa). A small circle of joint errors becomes an ellipse of foot errors. Its longest and shortest half-axes are J's **singular values** σmax and σmin; κ = σmax / σmin. κ = 1 means the foot is equally precise in every direction; a big κ means one direction is much sloppier (and near a singularity σmin → 0, so κ → ∞).
    
    Write `det_formula(θ1, θ2, θ3)` from the formula, and `kappa(M)` for any matrix M. numpy gives the singular values: `np.linalg.svd(M, compute_uv=False)`. The checker compares your formula with `np.linalg.det` of your own J.""",
            "ex2_h1": 'det_formula needs r: the same expression as in jacobian(). Then −r·L2·L3·sin θ3, with θ3 in radians.',
            "ex2_h2": '`sv = np.linalg.svd(M, compute_uv=False)` returns the singular values as an array. κ = sv.max() / sv.min().',
            "ex2_a": """```python
    def det_formula(theta1, theta2, theta3):
        r = L1 + L2 * np.cos(np.radians(theta2)) + L3 * np.cos(np.radians(theta2 - theta3))
        return -r * L2 * L3 * np.sin(np.radians(theta3))
    
    def kappa(M):
        sv = np.linalg.svd(M, compute_uv=False)
        return sv.max() / sv.min()
    ```""",
            "ex2_wait": 'Finish checkpoint 1 first: the formula is compared with det of your J.',
            "vs_det": '(compared with np.linalg.det of your J)',
            "ex2_after": "At home det J ≈ −1.57 × 10⁶ mm³/rad³, far from zero, and κ ≈ 3.4: the foot is about 3.4 times sloppier in one direction than in another. Notice the full 3×3 J and its side-view 2×2 part give the same κ here: the coxa's singular value, 162 mm/rad, sits between the other two.",
            "ex3_md": """## ✏️ 3 · Joint torques from the foot force
    
    **Torque** τ (tau) is a turning effort: force × lever arm. Each joint has one torque, so τ is a vector of three numbers.
    
    The foot pushes on the ground with a force **F** = (Fx, Fy, Fz) in newtons. When standing still on three feet (a tripod), each foot carries a third of the weight: our robot is about 2.2 kg, so 2.2 × 9.81 / 3 ≈ 7.2 N, pushing **down**: F = (0, 0, −7.2).
    
    The page derived **τ = Jᵀ · F** from power balance (servo power in = foot power out). Jᵀ is the **transpose**: rows and columns swapped, so entry j of Jᵀ·F is (column j of J) · F, the **dot product** a·b = a1·b1 + a2·b2 + a3·b3. With J in mm/rad and F in N, τ comes out in N·mm; divide by KGCM to get kg·cm.
    
    Write `torques(theta, F)` that returns the three torques in kg·cm. In numpy, `J.T` is the transpose and `@` multiplies a matrix by a vector.""",
            "ex3_h1": '`J = jacobian(*theta)` (the * unpacks the three angles). Then `J.T @ F`.',
            "ex3_h2": 'Turn F into an array first: `np.asarray(F, dtype=float)`. At home with F = (0, 0, −7.2) you should get about (0, −7.34, 2.51) kg·cm.',
            "ex3_a": """```python
    J = jacobian(*theta)
    return J.T @ np.asarray(F, dtype=float) / KGCM
    ```""",
            "ex3_after": "Read the home row: τ1 = 0 (a vertical force can't turn the coxa), τ2 ≈ −7.3 kg·cm (29% of stall), τ3 ≈ +2.5 kg·cm (10%). For a vertical force only J's **z row** matters, (0, u, −L3·cos(θ2 − θ3)): those are exactly the horizontal lever arms. So the femur's torque is just u × the load.",
            "ex4_md": """## ✏️ 4 · A map for choosing the stance
    
    The **stance** is where the feet stand relative to the body. In the side view (θ1 = 0) it is one point (u, z): u how far out from the femur joint, z how far below it. Every choice is a trade-off:
    - **Strong**: small femur torque, as a percentage of stall: τ2% = |τ2| / STALL × 100. Lower is better: less heat, less current, more reserve for walking.
    - **Precise**: small κ, the side-view condition number. Use the 2×2 part of J with rows x and z (0 and 2) and columns θ2 and θ3 (1 and 2): `J[[0, 2]][:, [1, 2]]`.
    - **Stable**: feet far out make a big support polygon (Stage 6). The map can't show that one; keep it in mind.
    
    Write the inside of the loop in `stance_map(us, zs, load)`. For each grid point: ask `ik(L1 + u, 0, z)` for the angles (skip the point if it returns None), then fill `tau2_pct[i, j]` and `kap[i, j]`. The foot presses down with `load` newtons.""",
            "ex4_h1": 'The foot target in the leg frame is (L1 + u, 0, z): u is measured from the femur joint, ik() wants x from the coxa axis. If `a is None`, `continue` skips to the next point.',
            "ex4_h2": '`torques(a, (0, 0, -load))[1]` is τ2 in kg·cm. For κ: `kappa(jacobian(*a)[[0, 2]][:, [1, 2]])`.',
            "ex4_a": """```python
    a = ik(L1 + u, 0, z)
    if a is None:
        continue
    J = jacobian(*a)
    tau2_pct[i, j] = abs(torques(a, (0, 0, -load))[1]) / STALL * 100
    kap[i, j] = kappa(J[[0, 2]][:, [1, 2]])
    ```""",
            "map_res": 'Your map on a 3 × 4 test grid (rows z = −130, −89.5, −40; columns u = 60, 100, 140, 200). — means unreachable.',
            "map_tau": '**τ2 (% of stall)**: notice each column is the same. τ2 = u × load depends only on u, not on the height.',
            "map_k": '**κ (side view)**: grows near the edges of the workspace, where the leg is almost straight or folded.',
            "why_label": 'Your stance and why (for you; not checked)',
            "why_ph": 'e.g. u = 100, z = −90: femur at ~29%, κ ≈ 3.4, body high enough to clear small bumps…',
            "r1_md": """## ★ Reward · Pick your stance
    
    Your `stance_map` on the whole side view: left, femur torque (blue = easy, orange = near stall); right, κ (blue = precise, orange = sloppy, capped at 12). The circle is the stance you choose with the sliders. Below, the robot stands there, with the femur torque of every leg while walking on a tripod (R1, R3 and L2 down, the others in the air). Write your choice and your reasons in the box above.""",
            "map_tau_t": 'femur torque, % of stall',
            "map_k_t": 'κ (side view)',
            "r1_none": "ik() can't reach that point within the joint limits. Move the sliders.",
            "bars_tri": '**Femur load, tripod** (three feet carry 7.2 N each):',
            "bars_six": 'Standing on all six feet (3.6 N each): **{p:.0f}%** per femur.',
            "r1_done": "Your stance: femur at **{tau:.0f}%** of stall on a tripod, κ ≈ **{k:.1f}**, body {h:.0f} mm above the feet. We kept the original firmware's stance, u ≈ 100, z ≈ −89.5: 29% and κ ≈ 3.4.",
            "st_pick": 'stance',
            "st_low": 'low (u 100, z −60)',
            "st_med": 'medium = home (u 100, z −89.5)',
            "st_wide": 'wide (u 140, z −89.5)',
            "robot_md": """## 🤖 Bonus · Does the current agree with the map?
    
    Stand the real robot in each stance through `utils/link.py` and read the battery current (a USB power meter or a clamp meter on the battery wire). Your map predicts the femur torque, and torque costs current: τ2 only depends on u, so **low** and **medium** should draw about the same, and **wide** clearly more. Does the robot rank them the way your map does? **Put it on the floor with space around it; keep the USB cable slack.**""",
            "robot_send": '▶ Stand in this stance',
            "robot_done": 'Standing at θ = {a} on every leg. Read the current now.',
            "outro": """## What you just learned
    - **Column j of J** is the foot's velocity when only joint j turns. Each entry is one partial derivative, in mm per radian.
    - **det J = 0** marks a singularity (r = 0 or a straight knee): the leg loses a direction. **κ** measures how lopsided the foot's precision is.
    - **τ = Jᵀ · F**: the same J that maps joint speed to foot speed maps foot force back to joint torque. For a vertical load, the femur torque is just u × load.
    - Choosing a stance is a trade-off between **strong**, **precise** and **stable**.
    
    **Next: Stage 5 · Body kinematics.** Keep all six feet still and move the body.""",
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
            "crumb": '阶段 4 · Jacobian 与静力学 · 练习',
            "intro": """# 关节动一点点，脚尖怎么动？📐
    
    **Jacobian** J 是一张把关节运动和脚尖运动联系起来的"变化率表"。有了它可以回答三个实际问题：脚尖能放得多准，腿在哪里会失去某个方向，每个舵机要使多大劲。你会分 **4 小块**来做：J 本身，它的行列式和条件数，关节扭矩，以及一张帮你选站姿的图。
    
    怎么做：修改标了 ✏️ 的代码格子，然后运行（Ctrl/Cmd + Enter）。每个格子下面的检查器会自动更新。每个公式都会和最朴素的**有限差分**对比（推一下关节，看脚尖动多少），所以你随时知道自己的推导对不对。四个全部通过后，解锁你的**站姿地图**，以及一个站在你选定位置的机器人。""",
            "given_md": """## 已经给你的东西
    
    - `fk(θ1, θ2, θ3)`：脚尖位置 (x, y, z)，单位 mm，来自阶段 1。公式里的几个量：
      - **r** = L1 + L2·cos θ2 + L3·cos(θ2 − θ3)：脚尖到 coxa 轴的水平距离；
      - **u** = r − L1：同一个距离，但从 **femur** 关节量起；
      - **z** = L2·sin θ2 + L3·sin(θ2 − θ3)：脚尖高度（负数 = 在髋关节下方）。
    - `ik(x, y, z)`：反过来，来自阶段 3（膝朝上），或者 None。
    - **STALL** = 25 kg·cm，舵机的堵转扭矩。**KGCM** = 98.0665：1 kg·cm 就是 9.80665 N 作用在离轴 10 mm 处，即 98.0665 N·mm。
    
    本 notebook 里传进函数的角度单位是**度**，但所有导数都是**每弧度**（mm/rad）。页面上的弧度说明讲了原因：d(sin θ)/dθ = cos θ 只在弧度下成立。""",
            "ex1_md": """## ✏️ 1 · 构造 J
    
    **偏导数** ∂x/∂θ2 是只转 θ2、θ1 和 θ3 不动时 x 变化的快慢。J 把九个偏导数放在一起：
    
    ```
          ⎡ ∂x/∂θ1  ∂x/∂θ2  ∂x/∂θ3 ⎤      第 1 行：x 对每个关节的响应
    J  =  ⎢ ∂y/∂θ1  ∂y/∂θ2  ∂y/∂θ3 ⎥      第 2 行：y
          ⎣ ∂z/∂θ1  ∂z/∂θ2  ∂z/∂θ3 ⎦      第 3 行：z
    ```
    
    **第 j 列**就是只转关节 j 时脚尖的速度（每弧度多少 mm）。把 FK 公式逐个求导；页面上已经推出了全部九项：
    
    ```
          ⎡ −r·sin θ1   −z·cos θ1   L3·sin(θ2−θ3)·cos θ1 ⎤
    J  =  ⎢  r·cos θ1   −z·sin θ1   L3·sin(θ2−θ3)·sin θ1 ⎥
          ⎣     0           u          −L3·cos(θ2−θ3)    ⎦
    ```
    
    写 `jacobian(θ1, θ2, θ3)`，返回这个 3×3 的 numpy 数组。检查器会拿它和**有限差分**比较：把一个关节推 ±10⁻⁶ rad，看 fk() 让脚尖移动多少，再除以推动量。这就是导数的定义，只是用数字来做。""",
            "ex1_h1": '先算出 r、z 和 u（角度用弧度），然后一行一行写出矩阵：`np.array([[...], [...], [...]])`。',
            "ex1_h2": '手算验证一项：∂z/∂θ2 = d/dθ2 (L2·sin θ2 + L3·sin(θ2 − θ3)) = L2·cos θ2 + L3·cos(θ2 − θ3) = u。在 home，J ≈ [[0, 89.5, −127.5], [162, 0, 0], [0, 100, −34.2]]。',
            "ex1_a": """```python
    t1, t2, t23 = np.radians(theta1), np.radians(theta2), np.radians(theta2 - theta3)
    r = L1 + L2 * np.cos(t2) + L3 * np.cos(t23)
    z = L2 * np.sin(t2) + L3 * np.sin(t23)
    u = r - L1
    return np.array([
        [-r * np.sin(t1), -z * np.cos(t1), L3 * np.sin(t23) * np.cos(t1)],
        [ r * np.cos(t1), -z * np.sin(t1), L3 * np.sin(t23) * np.sin(t1)],
        [0.0,              u,             -L3 * np.cos(t23)],
    ])
    ```""",
            "shape": 'jacobian() 返回的形状是 {s}，应该是 (3, 3)。',
            "fd_res": '你的 J 和有限差分在 {n} 个姿态上对比：最大的一项差 **{w:.1e} mm/rad**。',
            "fd_home": '你的 J 在 home (0°, 30°, 105°)，单位 mm/rad：',
            "fd_where": '差得最多的姿态是 {a}。有限差分在那里给出：',
            "ex2_md": """## ✏️ 2 · 行列式与条件数
    
    有两个数能概括 J 在某个姿态下"健康"与否。
    
    **行列式 det J。** 把一个由关节误差（边长 δθ1、δθ2、δθ3）组成的小方块送进 J，它会变成一个由脚尖误差组成的斜方块。det J 就是**体积**变化的倍数（带一个表示朝向的正负号）。如果 det J = 0，方块被压扁了：三列落在同一个平面里，脚尖有某个方向动不了，J 也没有逆矩阵。这样的姿态叫**奇异点**（singularity）。对我们的腿，页面上求得
    
    **det J = −r · L2 · L3 · sin θ3**
    
    所以在 r = 0（脚尖在 coxa 轴正下方）或 sin θ3 = 0（膝伸直）时为零。
    
    **条件数 κ**（kappa）。一个由关节误差组成的小圆，会变成一个由脚尖误差组成的椭圆。椭圆最长和最短的半轴就是 J 的**奇异值** σmax 和 σmin；κ = σmax / σmin。κ = 1 表示脚尖在各个方向一样准；κ 大表示某个方向差得多（接近奇异点时 σmin → 0，于是 κ → ∞）。
    
    照公式写 `det_formula(θ1, θ2, θ3)`，再写对任意矩阵 M 都适用的 `kappa(M)`。numpy 可以给出奇异值：`np.linalg.svd(M, compute_uv=False)`。检查器会拿你的公式和你自己的 J 的 `np.linalg.det` 对比。""",
            "ex2_h1": 'det_formula 需要 r：和 jacobian() 里的表达式一样。然后算 −r·L2·L3·sin θ3，θ3 用弧度。',
            "ex2_h2": '`sv = np.linalg.svd(M, compute_uv=False)` 以数组形式返回奇异值。κ = sv.max() / sv.min()。',
            "ex2_a": """```python
    def det_formula(theta1, theta2, theta3):
        r = L1 + L2 * np.cos(np.radians(theta2)) + L3 * np.cos(np.radians(theta2 - theta3))
        return -r * L2 * L3 * np.sin(np.radians(theta3))
    
    def kappa(M):
        sv = np.linalg.svd(M, compute_uv=False)
        return sv.max() / sv.min()
    ```""",
            "ex2_wait": '先完成检查点 1：这里要拿公式和你的 J 的行列式对比。',
            "vs_det": '（与你的 J 的 np.linalg.det 对比）',
            "ex2_after": '在 home，det J ≈ −1.57 × 10⁶ mm³/rad³，离零很远；κ ≈ 3.4：脚尖在某个方向上的误差约是另一个方向的 3.4 倍。注意完整的 3×3 J 和它侧视图的 2×2 部分在这里给出同样的 κ：coxa 对应的奇异值 162 mm/rad 正好夹在另外两个之间。',
            "ex3_md": """## ✏️ 3 · 由脚尖受力求关节扭矩
    
    **扭矩** τ（tau）是"转动的劲"：力 × 力臂。每个关节一个扭矩，所以 τ 是三个数组成的向量。
    
    脚尖以力 **F** = (Fx, Fy, Fz)（单位牛顿）压在地面上。三只脚站着不动时（tripod），每只脚承担三分之一的重量：我们的机器人约 2.2 kg，所以 2.2 × 9.81 / 3 ≈ 7.2 N，方向**向下**：F = (0, 0, −7.2)。
    
    页面上由功率守恒（舵机输入的功率 = 脚尖输出的功率）推出了 **τ = Jᵀ · F**。Jᵀ 是**转置**：行列互换，所以 Jᵀ·F 的第 j 项就是（J 的第 j 列）· F，即**点积** a·b = a1·b1 + a2·b2 + a3·b3。J 的单位是 mm/rad，F 是 N，所以 τ 的单位是 N·mm；除以 KGCM 换成 kg·cm。
    
    写 `torques(theta, F)`，返回三个以 kg·cm 为单位的扭矩。在 numpy 里 `J.T` 是转置，`@` 是矩阵乘向量。""",
            "ex3_h1": '`J = jacobian(*theta)`（* 把三个角拆开传进去）。然后 `J.T @ F`。',
            "ex3_h2": '先把 F 变成数组：`np.asarray(F, dtype=float)`。在 home，F = (0, 0, −7.2) 时你应该得到约 (0, −7.34, 2.51) kg·cm。',
            "ex3_a": """```python
    J = jacobian(*theta)
    return J.T @ np.asarray(F, dtype=float) / KGCM
    ```""",
            "ex3_after": '看 home 那一行：τ1 = 0（竖直的力转不动 coxa），τ2 ≈ −7.3 kg·cm（堵转的 29%），τ3 ≈ +2.5 kg·cm（10%）。对竖直的力，只有 J 的 **z 行** (0, u, −L3·cos(θ2 − θ3)) 起作用，它们正是水平方向的力臂。所以 femur 的扭矩就是 u × 载荷。',
            "ex4_md": """## ✏️ 4 · 一张选站姿的地图
    
    **站姿**（stance）指脚相对机身站在哪里。在侧视图（θ1 = 0）里它是一个点 (u, z)：u 是离 femur 关节多远，z 是在它下方多深。每种选择都是一种权衡：
    - **省力**：femur 扭矩小，以堵转扭矩的百分比表示：τ2% = |τ2| / STALL × 100。越低越好：发热少、电流小、留给行走的余量多。
    - **精确**：侧视图的条件数 κ 小。用 J 中行为 x 和 z（第 0、2 行）、列为 θ2 和 θ3（第 1、2 列）的 2×2 部分：`J[[0, 2]][:, [1, 2]]`。
    - **稳**：脚越往外，支撑多边形越大（阶段 6）。这一项地图上显示不出来，记在心里。
    
    写 `stance_map(us, zs, load)` 循环里面的部分。对每个网格点：用 `ik(L1 + u, 0, z)` 求关节角（返回 None 就跳过这个点），然后填 `tau2_pct[i, j]` 和 `kap[i, j]`。脚尖以 `load` 牛顿向下压。""",
            "ex4_h1": '腿坐标系里的脚尖目标是 (L1 + u, 0, z)：u 从 femur 关节量起，而 ik() 要的 x 从 coxa 轴量起。如果 `a is None`，用 `continue` 跳到下一个点。',
            "ex4_h2": '`torques(a, (0, 0, -load))[1]` 就是以 kg·cm 为单位的 τ2。κ：`kappa(jacobian(*a)[[0, 2]][:, [1, 2]])`。',
            "ex4_a": """```python
    a = ik(L1 + u, 0, z)
    if a is None:
        continue
    J = jacobian(*a)
    tau2_pct[i, j] = abs(torques(a, (0, 0, -load))[1]) / STALL * 100
    kap[i, j] = kappa(J[[0, 2]][:, [1, 2]])
    ```""",
            "map_res": '你的地图在 3 × 4 的测试网格上（行 z = −130、−89.5、−40；列 u = 60、100、140、200）。— 表示够不到。',
            "map_tau": '**τ2（占堵转的 %）**：注意每一列都一样。τ2 = u × 载荷，只取决于 u，与高度无关。',
            "map_k": '**κ（侧视图）**：在工作空间边缘、腿几乎伸直或折叠时变大。',
            "why_label": '你的站姿和理由（写给自己，不检查）',
            "why_ph": '例如 u = 100，z = −90：femur 约 29%，κ ≈ 3.4，机身够高能跨过小障碍……',
            "r1_md": """## ★ 奖励 · 选你的站姿
    
    你的 `stance_map` 铺满整个侧视图：左边是 femur 扭矩（蓝 = 轻松，橙 = 接近堵转）；右边是 κ（蓝 = 精确，橙 = 松垮，上限截在 12）。圆圈是你用滑块选的站姿。下面机器人就站在那里，旁边是 tripod 行走时（R1、R3、L2 着地，其余在空中）每条腿 femur 的扭矩。把你的选择和理由写在上面的文本框里。""",
            "map_tau_t": 'femur 扭矩，占堵转 %',
            "map_k_t": 'κ（侧视图）',
            "r1_none": 'ik() 在关节限位内够不到这个点。挪一下滑块。',
            "bars_tri": '**femur 负载，tripod**（三只脚各承担 7.2 N）：',
            "bars_six": '六只脚都着地时（各 3.6 N）：每个 femur **{p:.0f}%**。',
            "r1_done": '你的站姿：tripod 时 femur 为堵转的 **{tau:.0f}%**，κ ≈ **{k:.1f}**，机身比脚高 {h:.0f} mm。我们沿用了原固件的站姿 u ≈ 100、z ≈ −89.5：29%，κ ≈ 3.4。',
            "st_pick": '站姿',
            "st_low": '低（u 100，z −60）',
            "st_med": '中 = home（u 100，z −89.5）',
            "st_wide": '宽（u 140，z −89.5）',
            "robot_md": """## 🤖 附加 · 电流和地图一致吗？
    
    通过 `utils/link.py` 让真机器人依次站成每种姿态，读电池电流（USB 功率计，或在电池线上用钳形表）。你的地图预测了 femur 扭矩，而扭矩要靠电流：τ2 只取决于 u，所以**低**和**中**的电流应该差不多，**宽**明显更大。机器人的排序和你的地图一致吗？**把它放在四周有空间的地上；USB 线要留松。**""",
            "robot_send": '▶ 摆成这个站姿',
            "robot_done": '每条腿都站在 θ = {a}。现在读电流。',
            "outro": """## 你刚学到的
    - **J 的第 j 列**是只转关节 j 时脚尖的速度。每一项都是一个偏导数，单位是每弧度多少 mm。
    - **det J = 0** 标志奇异点（r = 0 或膝伸直）：腿失去一个方向。**κ** 衡量脚尖精度在各方向上有多不均匀。
    - **τ = Jᵀ · F**：把关节速度映射到脚尖速度的同一个 J，也把脚尖受力映射回关节扭矩。对竖直载荷，femur 扭矩就是 u × 载荷。
    - 选站姿是在**省力**、**精确**和**稳**之间权衡。
    
    **下一步：阶段 5 · 机身运动学。** 六只脚都不动，让机身动起来。""",
        },
    }
    return (TEXT,)


if __name__ == "__main__":
    app.run()
