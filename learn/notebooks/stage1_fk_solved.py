import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium", app_title="HexPod Academy · Stage 1 FK")


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
    _names = ["(r, z)", "fk", "table", "matrix"]
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
    L1, L2, L3 = 62.0, 76.0, 132.0                                   # coxa, femur, tibia (mm)
    LIMITS = {"theta1": (-45, 45), "theta2": (-75, 75), "theta3": (15, 165)}   # joint limits (degrees)
    return L1, L2, L3, LIMITS


@app.cell(hide_code=True)
def _(mo, t):
    mo.vstack([mo.md(t("ex1_md")), mo.accordion({t("hint") + " 1": mo.md(t("ex1_h1")), t("hint") + " 2": mo.md(t("ex1_h2")), t("answer"): mo.md(t("ex1_a"))})])
    return


@app.cell
def _(L1, L2, L3, np):
    def leg_plane(theta2, theta3):
        """Side view. Angles in degrees -> (r, z) in mm: horizontal distance from the coxa axis, and height."""
        # (reference solution)
        t2, t23 = np.radians(theta2), np.radians(theta2 - theta3)
        r = L1 + L2 * np.cos(t2) + L3 * np.cos(t23)
        z = L2 * np.sin(t2) + L3 * np.sin(t23)
        return r, z
    return (leg_plane,)


@app.cell(hide_code=True)
def _(check, leg_plane):
    ok1, _view = check(leg_plane, [((30, 105), (161.982, -89.5022)), ((0, 0), (270.0, 0.0)), ((0, 90), (138.0, -132.0)),
                                   ((60, 150), (100.0, -66.1821)), ((-45, 30), (149.9042, -181.2423)), ((75, 15), (147.6702, 187.7257))],
                       tol=0.01)
    _view
    return (ok1,)


@app.cell(hide_code=True)
def _(mo, t):
    mo.vstack([mo.md(t("ex2_md")), mo.accordion({t("hint") + " 1": mo.md(t("ex2_h1")), t("answer"): mo.md(t("ex2_a"))})])
    return


@app.cell
def _(leg_plane, np):
    def fk(theta1, theta2, theta3):
        """Joint angles (degrees) -> foot position np.array([x, y, z]) in mm, leg frame."""
        # (reference solution)
        r, z = leg_plane(theta2, theta3)
        t1 = np.radians(theta1)
        return np.array([r * np.cos(t1), r * np.sin(t1), z])
    return (fk,)


@app.cell(hide_code=True)
def _(check, fk):
    ok2, _view = check(fk, [((0, 30, 105), (161.982, 0.0, -89.5022)), ((30, 30, 105), (140.2806, 80.991, -89.5022)),
                            ((-45, -30, 60), (90.3809, -90.3809, -170.0)), ((20, 60, 150), (93.9693, 34.202, -66.1821))], tol=0.01)
    _view
    return (ok2,)


@app.cell(hide_code=True)
def _(mo, t):
    mo.vstack([mo.md(t("ex3_md")), mo.accordion({t("hint") + " 1": mo.md(t("ex3_h1")), t("hint") + " 2": mo.md(t("ex3_h2")), t("answer"): mo.md(t("ex3_a"))})])
    return


@app.cell
def _():
    # ✏️ Work these out on paper, then replace each None with (x, y, z) in mm.
    MY_TABLE = {(0, 90, 90): (194, 0, 76), (90, 0, 90): (0, 138, -132)}
    return (MY_TABLE,)


@app.cell(hide_code=True)
def _(MY_TABLE, check, fk, mo, t):
    _truth = {(0, 90, 90): (194.0, 0.0, 76.0), (90, 0, 90): (0.0, 138.0, -132.0)}
    _okH, _vH = check(lambda k: MY_TABLE.get(k), [((k,), v, f"{k} {t('by_hand')}") for k, v in _truth.items()], tol=0.5)
    _rows = [((0, 30, 105), (161.982, 0.0, -89.5022), "home"), ((0, 0, 0), (270.0, 0.0, 0.0), "straight"),
             ((0, 90, 90), (194.0, 0.0, 76.0)), ((90, 0, 90), (0.0, 138.0, -132.0)), ((30, 30, 105), (140.2806, 80.991, -89.5022)),
             ((-45, -30, 60), (90.3809, -90.3809, -170.0)), ((20, 60, 150), (93.9693, 34.202, -66.1821))]
    _okF, _vF = check(fk, _rows, tol=0.01)
    ok3 = _okH and _okF
    mo.vstack([mo.md(t("tbl_hand")), _vH, mo.md(t("tbl_fk")), _vF])
    return (ok3,)


@app.cell(hide_code=True)
def _(mo, t):
    mo.vstack([mo.md(t("ex4_md")), mo.accordion({t("hint") + " 1": mo.md(t("ex4_h1")), t("hint") + " 2": mo.md(t("ex4_h2")), t("answer"): mo.md(t("ex4_a"))})])
    return


@app.cell
def _(np):
    # ── Given: the three kinds of moves as 4×4 matrices (Stage 5 explains how they are built) ──
    def Rz(deg):
        c, s = np.cos(np.radians(deg)), np.sin(np.radians(deg))
        return np.array([[c, -s, 0, 0], [s, c, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])

    def Ry(deg):
        c, s = np.cos(np.radians(deg)), np.sin(np.radians(deg))
        return np.array([[c, 0, s, 0], [0, 1, 0, 0], [-s, 0, c, 0], [0, 0, 0, 1]])

    def Tx(d):
        T = np.eye(4)
        T[0, 3] = d
        return T
    return Rz, Ry, Tx


@app.cell
def _(L1, L2, L3, Ry, Rz, Tx, np):
    def fk_matrix(theta1, theta2, theta3):
        """Same answer as fk(), built as a chain of moves. Returns np.array([x, y, z])."""
        # (reference solution)
        T = Rz(theta1) @ Tx(L1) @ Ry(-theta2) @ Tx(L2) @ Ry(theta3) @ Tx(L3)
        return T[:3, 3]
    return (fk_matrix,)


@app.cell(hide_code=True)
def _(LIMITS, fk, fk_matrix, mo, np, ok2, t, verdict):
    def _agree():
        if not ok2:
            return False, mo.callout(mo.md(t("ex4_wait")), kind="neutral")
        _rng = np.random.default_rng(1)
        _worst, _err = 0.0, None
        for _ in range(200):
            _a = [_rng.uniform(*LIMITS[k]) for k in ("theta1", "theta2", "theta3")]
            try:
                _m = fk_matrix(*_a)
                if _m is None:
                    return False, mo.callout(mo.md("✏️ " + t("not_started")), kind="neutral")
                _worst = max(_worst, float(np.linalg.norm(np.asarray(_m, dtype=float) - fk(*_a))))
            except Exception as e:
                _err = f"{type(e).__name__}: {e}"
                break
        if _err:
            return False, verdict(False, ["❌ " + _err])
        _ok = _worst < 1e-9
        return _ok, verdict(_ok, [("✅ " if _ok else "❌ ") + t("agree").format(w=_worst)])

    ok4, _view = _agree()
    _view
    return (ok4,)


@app.cell(hide_code=True)
def _(mo, t):
    mo.md(t("r1_md"))
    return


@app.cell(hide_code=True)
def _(LIMITS, fk, json, mo, np, ok1, ok2, ok3, ok4, t):
    def _cloud(P):
        data = json.dumps(np.round(P, 1).tolist())
        return mo.iframe("""<!doctype html><html><head><meta charset='utf-8'><style>
        :root{--ink:#16202a;--muted:#5b6875;--bg:#fff}@media (prefers-color-scheme: dark){:root{--ink:#e3e9ef;--muted:#98a5b2;--bg:#17202a}}
        html,body{margin:0;background:var(--bg);font:12px monospace;color:var(--muted)}canvas{width:100%;height:100vh;display:block;cursor:grab;touch-action:none}
        #l{position:absolute;left:10px;top:8px}</style></head><body><div id='l'>drag to rotate</div><canvas id='c'></canvas><script>const P=""" + data + """;
        const cv=document.getElementById('c'),x=cv.getContext('2d');let az=-0.6,el=0.45,lx=null,ly=null;
        function fit(){const r=cv.getBoundingClientRect();cv.width=r.width*devicePixelRatio;cv.height=r.height*devicePixelRatio;draw()}
        cv.onpointerdown=e=>{lx=e.clientX;ly=e.clientY;cv.setPointerCapture(e.pointerId)};
        cv.onpointermove=e=>{if(lx==null)return;az+=(e.clientX-lx)*0.01;el=Math.max(-1.4,Math.min(1.4,el+(e.clientY-ly)*0.01));lx=e.clientX;ly=e.clientY;draw()};cv.onpointerup=()=>lx=null;
        function draw(){const W=cv.width,H=cv.height,s=Math.min(W,H)/420,cx=W*0.5,cy=H*0.42,ca=Math.cos(az),sa=Math.sin(az),ce=Math.cos(el),se=Math.sin(el);
          x.clearRect(0,0,W,H);const Q=P.map(p=>{const xr=p[0]*ca-p[1]*sa,yr=p[0]*sa+p[1]*ca;return [cx+s*xr,cy-s*(p[2]*ce+yr*se),yr*ce-p[2]*se,p[2]]}).sort((a,b)=>b[2]-a[2]);
          for(const q of Q){const h=(q[3]+200)/400;x.fillStyle=`hsl(${210-185*h},72%,52%)`;x.globalAlpha=0.55;x.fillRect(q[0]-1.5,q[1]-1.5,3,3)}
          x.globalAlpha=1;x.strokeStyle=getComputedStyle(document.documentElement).getPropertyValue('--ink');x.lineWidth=2*devicePixelRatio;
          const o=[cx,cy];[[80,0,0],[0,80,0],[0,0,80]].forEach((a,i)=>{const xr=a[0]*ca-a[1]*sa,yr=a[0]*sa+a[1]*ca;x.beginPath();x.moveTo(o[0],o[1]);x.lineTo(cx+s*xr,cy-s*(a[2]*ce+yr*se));x.stroke();
            x.fillStyle=x.strokeStyle;x.font=(12*devicePixelRatio)+'px monospace';x.fillText('xyz'[i],cx+s*xr*1.15,cy-s*(a[2]*ce+yr*se)*1.15)})}
        addEventListener('resize',fit);fit();</script></body></html>""", height="420px")

    def _side(R, Z):
        W, H, s = 480, 420, 1.0
        X = lambda r: 170 + r * s
        Y = lambda z: 205 - z * s
        g = [f"<svg viewBox='0 0 {W} {H}' style='width:100%;max-width:480px;font:11px monospace'>",
             f"<line x1='{X(-160)}' y1='{Y(0)}' x2='{X(295)}' y2='{Y(0)}' stroke='#8886'/><line x1='{X(0)}' y1='{Y(195)}' x2='{X(0)}' y2='{Y(-210)}' stroke='#8886'/>",
             f"<text x='{X(295)}' y='{Y(0) - 6}' text-anchor='end' fill='currentColor'>r</text><text x='{X(0) + 6}' y='{Y(195) + 10}' fill='currentColor'>z</text>"]
        g += [f"<circle cx='{X(r):.1f}' cy='{Y(z):.1f}' r='1.6' fill='#2a6fb0' opacity='.45'/>" for r, z in zip(R, Z)]
        g.append(f"<circle cx='{X(162)}' cy='{Y(-89.5)}' r='6' fill='none' stroke='#d9771f' stroke-width='2.5'/><text x='{X(162) + 10}' y='{Y(-89.5) + 4}' fill='#d9771f'>home</text></svg>")
        return mo.Html("".join(g))

    if not (ok1 and ok2 and ok3 and ok4):
        _out = mo.callout(mo.md("🔒 " + t("r_locked")), kind="neutral")
    else:
        _rng = np.random.default_rng(7)
        _A = np.column_stack([_rng.uniform(*LIMITS[k], 5000) for k in ("theta1", "theta2", "theta3")])
        _P = np.array([fk(*a) for a in _A])
        _r = np.hypot(_P[:, 0], _P[:, 1]) * np.sign(_P[:, 0])
        _out = mo.vstack([_cloud(_P[:2500]), mo.md(t("r1_side")), _side(_r[::2], _P[::2, 2]), mo.callout(mo.md(t("r1_done").format(
            zlo=_P[:, 2].min(), zhi=_P[:, 2].max(), rmax=np.hypot(_P[:, 0], _P[:, 1]).max())), kind="success")])
    _out
    return


@app.cell(hide_code=True)
def _(mo, t):
    s1 = mo.ui.slider(-45, 45, value=0, step=1, label="θ1 (°)", show_value=True)
    s2 = mo.ui.slider(-75, 75, value=30, step=1, label="θ2 (°)", show_value=True)
    s3 = mo.ui.slider(15, 165, value=105, step=1, label="θ3 (°)", show_value=True)
    mo.vstack([mo.md(t("r2_md")), mo.hstack([s1, s2, s3], wrap=True)])
    return s1, s2, s3


@app.cell(hide_code=True)
def _(fk, mo, np, ok1, ok2, ok3, ok4, player, s1, s2, s3, t):
    if not (ok1 and ok2 and ok3 and ok4):
        _out = mo.callout(mo.md("🔒 " + t("r_locked")), kind="neutral")
    else:
        _p = np.asarray(fk(s1.value, s2.value, s3.value), dtype=float)
        _box = [(_p + [dx, dy, 0]).round(2).tolist() for dx, dy in ((-6, -6), (6, -6), (6, 6), (-6, 6))]
        _cfg = {"mode": "leg", "angles": [[[s1.value, s2.value, s3.value]]], "target": _box, "fps": 1,
                "labels": [f"your fk(): ({_p[0]:.1f}, {_p[1]:.1f}, {_p[2]:.1f}) mm"], "cy": 0.6}
        _out = mo.vstack([player(_cfg, 340), mo.md(t("r2_note"))])
    _out
    return


@app.cell(hide_code=True)
def _(IN_BROWSER, mo, t):
    leg_pick = mo.ui.dropdown(options={"R1": 0, "R2": 1, "R3": 2, "L1": 3, "L2": 4, "L3": 5}, value="R2", label=t("leg"))
    robot_on = mo.ui.switch(label=t("robot_switch"))
    send = mo.ui.run_button(label=t("robot_send"))
    mo.vstack([mo.md(t("robot_md")),
               mo.callout(mo.md(t("robot_browser")), kind="neutral") if IN_BROWSER else mo.hstack([leg_pick, robot_on, send], justify="start")])
    return leg_pick, robot_on, send


@app.cell(hide_code=True)
def _(IN_BROWSER, fk, leg_pick, mo, np, ok2, robot_on, s1, s2, s3, send, t):
    mo.stop(IN_BROWSER or not send.value)
    mo.stop(not robot_on.value, mo.callout(mo.md(t("robot_need_switch")), kind="warn"))
    mo.stop(not ok2, mo.callout(mo.md(t("r_locked")), kind="warn"))

    import pathlib, sys as _sys
    _code_dir = pathlib.Path(mo.notebook_dir()).resolve().parents[1]           # .../code
    if str(_code_dir) not in _sys.path:
        _sys.path.insert(0, str(_code_dir))
    from utils.link import Link

    _home = np.array([0, 30, 105] * 6, dtype=float)
    _goal = _home.copy()
    _goal[3 * leg_pick.value: 3 * leg_pick.value + 3] = [s1.value, s2.value, s3.value]
    _link = Link()
    try:
        _link.move_to(_home, 2)
        _link.move_to(_goal, 2)
    finally:
        _link.close()
    _p = fk(s1.value, s2.value, s3.value)
    mo.callout(mo.md(t("robot_done").format(x=_p[0], y=_p[1], z=_p[2])), kind="success")
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
            "crumb": 'Stage 1 · Forward kinematics · practice',
            "intro": """# Where is the foot? 🦵
    
    **Forward kinematics** (FK) answers one question: given the three joint angles, where is the foot? You'll build `fk()` in **4 small pieces**: the side view, the top view, a check table you partly fill in by hand, and the same answer again as a chain of matrices.
    
    How to work: edit the code cells marked ✏️, then run them (Ctrl/Cmd + Enter). The checker under each one updates on its own. If you're stuck, open the hints one at a time; the last one is the full answer. Pass all four to unlock your leg's **3D workspace** and a leg you can drive with sliders.""",
            "given_md": """## What you're given
    
    **The leg frame.** Every position on this page is three numbers (x, y, z) in millimetres, measured from the **coxa axis** (the vertical axis the whole leg turns about) at the height of that joint:
    - **x** points straight out along the leg when θ1 = 0, **y** points to the leg's left, **z** points up. These three directions form a right-handed frame (Step 1 of the page).
    
    **The joints**, all in degrees:
    - **θ1** (coxa): swings the whole leg left/right about z. 0° = straight out; positive = toward +y.
    - **θ2** (femur): tilts the femur up/down, measured from the horizontal. Positive = up.
    - **θ3** (knee): how far the tibia is bent away from the femur's direction. 0° = straight, 90° = right angle. It is a **relative** angle, so the tibia's own direction, measured from the horizontal, is **θ2 − θ3**.
    
    **The links**: L1 = 62 mm (coxa), L2 = 76 mm (femur), L3 = 132 mm (tibia). **LIMITS** is the range each servo may move without hitting anything.""",
            "ex1_md": """## ✏️ 1 · The side view
    
    Forget θ1 for now and look at the leg from the side. The picture is a 2D arm with three links. Two new names:
    - **r**: the foot's horizontal distance from the coxa axis.
    - **z**: the foot's height relative to the coxa joint (negative = below).
    
    Walk out along the links one after another. Each link is an arrow with a length L and a direction φ (phi) measured from the horizontal; its horizontal piece is **L·cos φ** and its vertical piece **L·sin φ** (the cos/sin "shadow" from the page). The three directions are:
    - coxa: 0 (it is horizontal), femur: θ2, tibia: θ2 − θ3.
    
    Add the horizontal pieces to get r and the vertical pieces to get z. Write `leg_plane(theta2, theta3)` that returns `(r, z)`. numpy's `np.cos` and `np.sin` want **radians**: convert with `np.radians(...)`.""",
            "ex1_h1": 'r = L1 + L2·cos θ2 + L3·cos(θ2 − θ3). z has no coxa term (the coxa is level): z = L2·sin θ2 + L3·sin(θ2 − θ3).',
            "ex1_h2": 'Convert both angles first: `t2 = np.radians(theta2)` and `t23 = np.radians(theta2 - theta3)`. At home (30°, 105°) you should get about (162.0, −89.5).',
            "ex1_a": """```python
    t2, t23 = np.radians(theta2), np.radians(theta2 - theta3)
    r = L1 + L2 * np.cos(t2) + L3 * np.cos(t23)
    z = L2 * np.sin(t2) + L3 * np.sin(t23)
    return r, z
    ```""",
            "ex2_md": """## ✏️ 2 · The top view
    
    Now let θ1 swing the whole side-view plane about the vertical axis. Seen from above, the foot is at distance r from the coxa axis in direction θ1. That is a point given in **polar coordinates** (a distance and a direction); we need **Cartesian coordinates** (x, y). Same shadow trick: x is r's shadow on the x axis, y its shadow on the y axis. The height z doesn't change at all when the leg swings sideways.
    
    Write `fk(theta1, theta2, theta3)` that calls your `leg_plane` and returns `np.array([x, y, z])`.""",
            "ex2_h1": 'x = r·cos θ1, y = r·sin θ1, z = z. Again convert θ1 to radians first.',
            "ex2_a": """```python
    r, z = leg_plane(theta2, theta3)
    t1 = np.radians(theta1)
    return np.array([r * np.cos(t1), r * np.sin(t1), z])
    ```""",
            "ex3_md": """## ✏️ 3 · A check table, partly by hand
    
    A test is only as good as its expected values. So before trusting the checker, work out **two rows yourself, on paper**, and draw the leg for each:
    
    1. **(θ1, θ2, θ3) = (0°, 90°, 90°)**: the femur points straight up; the knee bends 90°, so the tibia points horizontally (direction 90° − 90° = 0°).
    2. **(90°, 0°, 90°)**: the femur is level, the tibia points straight down (0° − 90° = −90°), and the coxa has swung the whole leg 90° to the left.
    
    Type your answers into `MY_TABLE` as (x, y, z). The checker compares them with the truth (to 0.5 mm), then runs your `fk()` on all seven rows, including home and the stretched-out leg.""",
            "ex3_h1": 'Row 1: r = 62 + 76·cos 90° + 132·cos 0° = 62 + 0 + 132. z = 76·sin 90° + 132·sin 0° = 76. θ1 = 0, so y = 0 and x = r.',
            "ex3_h2": 'Row 2: r = 62 + 76 + 132·cos(−90°) = 138, z = 0 + 132·sin(−90°) = −132. θ1 = 90° turns r onto the y axis: x = 0, y = 138.',
            "ex3_a": """```python
    MY_TABLE = {(0, 90, 90): (194, 0, 76), (90, 0, 90): (0, 138, -132)}
    ```""",
            "by_hand": '(by hand)',
            "tbl_hand": '**Your hand-worked rows**',
            "tbl_fk": '**Your fk() on all seven rows**',
            "ex4_md": """## ✏️ 4 · The same leg as a chain of moves
    
    The page described FK as a list of moves that carry a little coordinate frame from the coxa axis to the foot. Each move is relative to wherever the previous one left the frame:
    
    **turn θ1 about z → slide L1 along x → tilt by θ2 → slide L2 → bend by θ3 → slide L3**
    
    A computer stores each move as a **4×4 matrix**. You don't need to know how it's built yet (Stage 5 explains it); you need two facts:
    1. **Multiplying** two of these matrices, A @ B (`@` is numpy's matrix product), means "do A, then do B in the frame A left you in". So the whole chain is one product, read left to right.
    2. In the result T, the **top three entries of the last column**, `T[:3, 3]`, are where the frame's origin ended up, measured in the starting frame. After the last slide, that origin is the foot.
    
    The three helpers are given: `Rz(deg)` turns about z, `Ry(deg)` turns about y, `Tx(d)` slides d mm along x. One sign to watch: a positive turn about y tips x **down** (right-hand rule), while θ2 counts **up** as positive, so the femur tilt is `Ry(-theta2)`. The knee bends the tibia down, which is `Ry(+theta3)`.
    
    Write `fk_matrix(theta1, theta2, theta3)`. The checker compares it with your `fk()` on 200 random legal poses; they must agree to 10⁻⁹ mm.""",
            "ex4_h1": 'T = Rz(θ1) @ Tx(L1) @ Ry(−θ2) @ Tx(L2) @ Ry(θ3) @ Tx(L3). Read it as the sentence above.',
            "ex4_h2": "Return only the position: `T[:3, 3]`. If you're off by a sign in z, check the signs inside the two Ry calls.",
            "ex4_a": """```python
    T = Rz(theta1) @ Tx(L1) @ Ry(-theta2) @ Tx(L2) @ Ry(theta3) @ Tx(L3)
    return T[:3, 3]
    ```""",
            "ex4_wait": 'Finish checkpoint 2 first: this one compares with your fk().',
            "agree": 'fk_matrix() vs fk() on 200 random legal poses: worst difference **{w:.1e} mm**.',
            "r1_md": """## ★ Reward 1 · Your leg's workspace
    
    The **workspace** is every point the foot can reach. Your `fk()` now runs on 5,000 random legal joint angles and plots each foot position. Drag to rotate; colour shows height (blue low, orange high).""",
            "r1_side": 'The same points from the side (horizontal: r with the sign of x; vertical: z). The thick crescent comes from the **joint limits**, not just the link lengths. The orange circle is home.',
            "r1_done": 'Your fk() placed 5,000 feet. Height range: {zlo:.0f} to {zhi:.0f} mm; farthest reach: {rmax:.0f} mm from the coxa axis.',
            "r2_md": """## ★★ Reward 2 · Drive the leg
    Move the sliders. The leg is drawn by the page's own renderer; the small dashed square is where **your** `fk()` says the foot is. If your FK is right, the foot always sits inside the square. Drag to rotate.""",
            "r2_note": 'This is exactly what the robot does with every command: three angles in, one foot position out.',
            "leg": 'leg',
            "robot_md": """## 🤖 Bonus · Check it with a ruler
    
    Same three angles from the sliders above, sent to one leg of the real robot through `utils/link.py`; the other five legs stay at home. Then measure the foot from the coxa axis with a ruler and compare with your `fk()`. Expect a few mm of error until Stage 2 calibrates the joints. **Keep the robot hanging or its feet clear of the table.**""",
            "robot_send": '▶ Send the angles',
            "robot_done": "Sent. Your fk() says the foot is at ({x:.1f}, {y:.1f}, {z:.1f}) mm in that leg's frame. Measure it!",
            "outro": """## What you just learned
    - FK in the side view is **adding arrows**: each link contributes L·cos and L·sin of its absolute direction (0, θ2, θ2 − θ3).
    - The coxa only **turns** that plane: polar (r, θ1) to Cartesian (x, y); z doesn't change.
    - The same answer comes from a **chain of 4×4 matrices**, read left to right. That form scales to many joints and to a moving body (Stage 5).
    - The **workspace** is shaped by the joint limits as much as by the link lengths.
    
    **Next: Stage 2 · Calibration.** The math says 30°; how do we make the servo agree?""",
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
            "crumb": '阶段 1 · 正运动学 · 练习',
            "intro": """# 脚尖在哪？🦵
    
    **正运动学**（forward kinematics，FK）只回答一个问题：给定三个关节角，脚尖在哪里？你会分 **4 小块**拼出 `fk()`：侧视图、俯视图、一张部分要你手算的检查表，以及用矩阵链再算一遍同样的答案。
    
    怎么做：修改标了 ✏️ 的代码格子，然后运行（Ctrl/Cmd + Enter）。每个格子下面的检查器会自动更新。卡住了就一条一条展开提示，最后一条是完整答案。四个全部通过后，解锁这条腿的 **3D 工作空间**，以及一条可以用滑块驱动的腿。""",
            "given_md": """## 已经给你的东西
    
    **腿坐标系。** 本页的每个位置都是三个数 (x, y, z)，单位毫米，从 **coxa 轴**（整条腿绕着转的那根竖直轴）在这个关节的高度处量起：
    - θ1 = 0 时 **x** 沿着腿笔直向外，**y** 指向腿的左边，**z** 向上。这三个方向构成右手坐标系（页面第 1 步）。
    
    **关节**，单位都是度：
    - **θ1**（coxa）：让整条腿绕 z 轴左右摆。0° = 正前方；正 = 转向 +y。
    - **θ2**（femur）：让 femur 上下摆，从水平线量起。正 = 向上。
    - **θ3**（膝）：tibia 相对 femur 的方向弯过去多少。0° = 伸直，90° = 直角。它是**相对**角，所以 tibia 自身从水平线量起的方向是 **θ2 − θ3**。
    
    **连杆**：L1 = 62 mm（coxa），L2 = 76 mm（femur），L3 = 132 mm（tibia）。**LIMITS** 是每个舵机不会撞到东西的活动范围。""",
            "ex1_md": """## ✏️ 1 · 侧视图
    
    先不管 θ1，从侧面看这条腿。它就是一个有三段连杆的平面机械臂。两个新名字：
    - **r**：脚尖到 coxa 轴的水平距离。
    - **z**：脚尖相对 coxa 关节的高度（负数 = 在下方）。
    
    沿着连杆一段接一段往外走。每段连杆是一个箭头，长度为 L，方向为 φ（phi，从水平线量起）；它的水平分量是 **L·cos φ**，竖直分量是 **L·sin φ**（页面上讲的 cos/sin "影子"）。三段的方向分别是：
    - coxa：0（它是水平的），femur：θ2，tibia：θ2 − θ3。
    
    把水平分量加起来得到 r，竖直分量加起来得到 z。写 `leg_plane(theta2, theta3)`，返回 `(r, z)`。numpy 的 `np.cos` 和 `np.sin` 要的是**弧度**：用 `np.radians(...)` 转换。""",
            "ex1_h1": 'r = L1 + L2·cos θ2 + L3·cos(θ2 − θ3)。z 没有 coxa 项（coxa 是水平的）：z = L2·sin θ2 + L3·sin(θ2 − θ3)。',
            "ex1_h2": '先把两个角都转成弧度：`t2 = np.radians(theta2)`，`t23 = np.radians(theta2 - theta3)`。在 home (30°, 105°) 你应该得到约 (162.0, −89.5)。',
            "ex1_a": """```python
    t2, t23 = np.radians(theta2), np.radians(theta2 - theta3)
    r = L1 + L2 * np.cos(t2) + L3 * np.cos(t23)
    z = L2 * np.sin(t2) + L3 * np.sin(t23)
    return r, z
    ```""",
            "ex2_md": """## ✏️ 2 · 俯视图
    
    现在让 θ1 把整个侧视平面绕竖直轴转过去。从上往下看，脚尖在离 coxa 轴 r 远、方向为 θ1 的地方。这是用**极坐标**（一个距离加一个方向）给出的点；我们需要**直角坐标** (x, y)。还是影子的办法：x 是 r 在 x 轴上的影子，y 是在 y 轴上的影子。腿左右摆时高度 z 完全不变。
    
    写 `fk(theta1, theta2, theta3)`，调用你的 `leg_plane`，返回 `np.array([x, y, z])`。""",
            "ex2_h1": 'x = r·cos θ1，y = r·sin θ1，z = z。同样先把 θ1 转成弧度。',
            "ex2_a": """```python
    r, z = leg_plane(theta2, theta3)
    t1 = np.radians(theta1)
    return np.array([r * np.cos(t1), r * np.sin(t1), z])
    ```""",
            "ex3_md": """## ✏️ 3 · 检查表，部分手算
    
    测试的好坏取决于期望值对不对。所以在相信检查器之前，先**在纸上自己算两行**，并把每个姿态的腿画出来：
    
    1. **(θ1, θ2, θ3) = (0°, 90°, 90°)**：femur 竖直朝上；膝弯 90°，所以 tibia 水平（方向 90° − 90° = 0°）。
    2. **(90°, 0°, 90°)**：femur 水平，tibia 竖直朝下（0° − 90° = −90°），而 coxa 把整条腿向左转了 90°。
    
    把答案以 (x, y, z) 的形式填进 `MY_TABLE`。检查器先把它们和真值比较（误差 0.5 mm 以内），再用你的 `fk()` 跑全部七行，包括 home 和完全伸直的腿。""",
            "ex3_h1": '第 1 行：r = 62 + 76·cos 90° + 132·cos 0° = 62 + 0 + 132。z = 76·sin 90° + 132·sin 0° = 76。θ1 = 0，所以 y = 0，x = r。',
            "ex3_h2": '第 2 行：r = 62 + 76 + 132·cos(−90°) = 138，z = 0 + 132·sin(−90°) = −132。θ1 = 90° 把 r 转到 y 轴上：x = 0，y = 138。',
            "ex3_a": """```python
    MY_TABLE = {(0, 90, 90): (194, 0, 76), (90, 0, 90): (0, 138, -132)}
    ```""",
            "by_hand": '（手算）',
            "tbl_hand": '**你手算的两行**',
            "tbl_fk": '**你的 fk() 跑全部七行**',
            "ex4_md": """## ✏️ 4 · 把同一条腿写成一串移动
    
    页面上把 FK 描述成一串移动，把一个小坐标系从 coxa 轴一路搬到脚尖。每一步都是相对于上一步把坐标系留下的位置和朝向来做的：
    
    **绕 z 转 θ1 → 沿 x 滑 L1 → 俯仰 θ2 → 滑 L2 → 弯 θ3 → 滑 L3**
    
    计算机把每一步存成一个 **4×4 矩阵**。现在还不需要知道它怎么构造（阶段 5 会讲），只需要两个事实：
    1. 两个这样的矩阵**相乘** A @ B（`@` 是 numpy 的矩阵乘法），意思是"先做 A，再在 A 留下的坐标系里做 B"。所以整串移动就是一个连乘，从左往右读。
    2. 结果 T 的**最后一列的前三个元素** `T[:3, 3]`，就是坐标系原点最后到了哪里，在起始坐标系中量。最后一次滑动之后，这个原点就是脚尖。
    
    三个辅助函数已经给好：`Rz(deg)` 绕 z 转，`Ry(deg)` 绕 y 转，`Tx(d)` 沿 x 滑 d mm。注意一个符号：绕 y 的正向转动会让 x 轴**向下**倾（右手定则），而 θ2 以**向上**为正，所以 femur 的俯仰是 `Ry(-theta2)`。膝让 tibia 向下弯，是 `Ry(+theta3)`。
    
    写 `fk_matrix(theta1, theta2, theta3)`。检查器在 200 个随机合法姿态上把它和你的 `fk()` 对比，两者必须一致到 10⁻⁹ mm。""",
            "ex4_h1": 'T = Rz(θ1) @ Tx(L1) @ Ry(−θ2) @ Tx(L2) @ Ry(θ3) @ Tx(L3)。照上面那句话读。',
            "ex4_h2": '只返回位置：`T[:3, 3]`。如果 z 的符号反了，检查两个 Ry 里的符号。',
            "ex4_a": """```python
    T = Rz(theta1) @ Tx(L1) @ Ry(-theta2) @ Tx(L2) @ Ry(theta3) @ Tx(L3)
    return T[:3, 3]
    ```""",
            "ex4_wait": '先完成检查点 2：这里要和你的 fk() 对比。',
            "agree": 'fk_matrix() 与 fk() 在 200 个随机合法姿态上的最大差距：**{w:.1e} mm**。',
            "r1_md": """## ★ 奖励 1 · 你的腿的工作空间
    
    **工作空间**（workspace）是脚尖能到达的所有点。你的 `fk()` 现在在 5000 组随机合法关节角上运行，把每个脚尖位置画出来。拖动可以旋转；颜色表示高度（蓝低橙高）。""",
            "r1_side": '同样的点从侧面看（横轴：带 x 符号的 r；纵轴：z）。那道粗月牙形是**关节限位**造成的，不只是连杆长度。橙色圆圈是 home。',
            "r1_done": '你的 fk() 算出了 5000 个脚尖位置。高度范围：{zlo:.0f} 到 {zhi:.0f} mm；最远离 coxa 轴 {rmax:.0f} mm。',
            "r2_md": """## ★★ 奖励 2 · 驱动这条腿
    拖动滑块。腿由页面自己的渲染器画出；那个小虚线方框是**你的** `fk()` 算出的脚尖位置。如果你的 FK 对，脚尖永远在方框里。拖动可以旋转。""",
            "r2_note": '机器人对每一条指令做的正是这件事：输入三个角，输出一个脚尖位置。',
            "leg": '腿',
            "robot_md": """## 🤖 附加 · 用尺子验证
    
    把上面滑块的三个角，通过 `utils/link.py` 发给真机器人的一条腿；其余五条腿保持 home。然后用尺子量脚尖到 coxa 轴的距离，和你的 `fk()` 对比。在阶段 2 标定关节之前，预计会有几毫米误差。**让机器人悬空，或者让它的脚离开桌面。**""",
            "robot_send": '▶ 发送角度',
            "robot_done": '已发送。你的 fk() 说脚尖在这条腿坐标系中的 ({x:.1f}, {y:.1f}, {z:.1f}) mm。量一量！',
            "outro": """## 你刚学到的
    - 侧视图里的 FK 就是**箭头相加**：每段连杆贡献它绝对方向（0、θ2、θ2 − θ3）的 L·cos 和 L·sin。
    - coxa 只是把这个平面**转过去**：极坐标 (r, θ1) 变成直角坐标 (x, y)；z 不变。
    - 同一个答案也可以由**一串 4×4 矩阵**从左往右相乘得到。这种写法可以推广到很多关节和会动的机身（阶段 5）。
    - **工作空间**的形状既取决于连杆长度，也同样取决于关节限位。
    
    **下一步：阶段 2 · 标定。** 数学说 30°，怎样让舵机也同意？""",
        },
    }
    return (TEXT,)


if __name__ == "__main__":
    app.run()
