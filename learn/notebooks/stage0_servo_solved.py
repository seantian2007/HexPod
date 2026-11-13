import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium", app_title="HexPod Academy · Stage 0 Servos")


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
    _names = ["us ↔ θ", "fit", "ticks", "power"]
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
    # ── Given (from the Stage 0 page) — you don't need to change anything here ──
    K = 0.0901          # degrees per microsecond: the slope we measured
    DATA = np.array([   # (pulse width in µs, protractor reading in degrees), our 21 measurements
        (500, 166.5), (600, 175), (700, 185), (800, 194.5), (900, 203), (1000, 212), (1100, 221),
        (1200, 230), (1300, 239), (1400, 247.5), (1500, 256.5), (1600, 265), (1700, 274.5), (1800, 283),
        (1900, 292), (2000, 301), (2100, 310), (2200, 319.7), (2300, 329), (2400, 339), (2500, 348)])
    PULSES, READINGS = DATA[:, 0], DATA[:, 1]
    return K, PULSES, READINGS


@app.cell(hide_code=True)
def _(PULSES, READINGS, mo, np, t):
    def scatter_svg(x, y, line=None, resid=False):
        """A small x-y plot as SVG. line = (a, b) draws y = a·x + b."""
        W, H, l, r, top, bot = 640, 260, 56, 16, 14, 40
        x0, x1 = 400, 2600
        y0, y1 = (float(np.min(y)) - 1, float(np.max(y)) + 1) if resid else (150, 360)
        X = lambda v: l + (v - x0) / (x1 - x0) * (W - l - r)
        Y = lambda v: H - bot - (v - y0) / (y1 - y0) * (H - top - bot)
        out = [f"<svg viewBox='0 0 {W} {H}' style='width:100%;max-width:640px;font:11px monospace'>"]
        for v in range(500, 2600, 500):
            out.append(f"<line x1='{X(v):.1f}' y1='{top}' x2='{X(v):.1f}' y2='{H - bot}' stroke='#8884'/>"
                       f"<text x='{X(v):.1f}' y='{H - bot + 14}' text-anchor='middle' fill='currentColor'>{v}</text>")
        ticks = np.linspace(y0, y1, 5)
        for v in ticks:
            out.append(f"<line x1='{l}' y1='{Y(v):.1f}' x2='{W - r}' y2='{Y(v):.1f}' stroke='#8882'/>"
                       f"<text x='{l - 6}' y='{Y(v) + 4:.1f}' text-anchor='end' fill='currentColor'>{v:.1f}</text>")
        if resid:
            out.append(f"<line x1='{l}' y1='{Y(0):.1f}' x2='{W - r}' y2='{Y(0):.1f}' stroke='#d9771f' stroke-width='1.5'/>")
            for a, b in zip(x, y):
                out.append(f"<line x1='{X(a):.1f}' y1='{Y(0):.1f}' x2='{X(a):.1f}' y2='{Y(b):.1f}' stroke='#2a6fb0' stroke-width='2'/>")
        if line is not None:
            a, b = line
            out.append(f"<line x1='{X(x0):.1f}' y1='{Y(a * x0 + b):.1f}' x2='{X(x1):.1f}' y2='{Y(a * x1 + b):.1f}' stroke='#d9771f' stroke-width='2'/>")
        for a, b in zip(x, y):
            out.append(f"<circle cx='{X(a):.1f}' cy='{Y(b):.1f}' r='3.5' fill='#2a6fb0'/>")
        out.append(f"<text x='{W - r}' y='{H - 6}' text-anchor='end' fill='currentColor'>µs</text></svg>")
        return mo.Html("".join(out))

    mo.vstack([scatter_svg(PULSES, READINGS), mo.md(t("data_cap"))])
    return (scatter_svg,)


@app.cell(hide_code=True)
def _(mo, t):
    mo.vstack([mo.md(t("ex1_md")), mo.accordion({t("hint") + " 1": mo.md(t("ex1_h1")), t("hint") + " 2": mo.md(t("ex1_h2")), t("answer"): mo.md(t("ex1_a"))})])
    return


@app.cell
def _(K):
    def pulse_to_angle(us, us0, s):
        """Pulse width (µs) -> joint angle (degrees), for a joint with zero pulse us0 and direction s."""
        # (reference solution)
        return s * K * (us - us0)

    def angle_to_pulse(theta, us0, s):
        """Joint angle (degrees) -> pulse width (µs). The inverse of pulse_to_angle."""
        # (reference solution)
        return us0 + theta / (s * K)
    return angle_to_pulse, pulse_to_angle


@app.cell(hide_code=True)
def _(angle_to_pulse, check, mo, pulse_to_angle):
    _okA, _vA = check(pulse_to_angle, [((1681, 1570, 1), 10.0011), ((1349, 1460, -1), 10.0011), ((1500, 1500, 1), 0.0),
                                       ((500, 1500, 1), -90.1), ((2500, 1500, -1), -90.1)], tol=0.001)
    _okB, _vB = check(angle_to_pulse, [((10, 1570, 1), 1680.9878), ((10, 1460, -1), 1349.0122), ((0, 1530, 1), 1530.0),
                                       ((-45, 1500, 1), 1000.5549), ((90, 1500, -1), 501.1099)], tol=0.001)
    ok1 = _okA and _okB
    mo.vstack([mo.md("`pulse_to_angle`"), _vA, mo.md("`angle_to_pulse`"), _vB])
    return (ok1,)


@app.cell(hide_code=True)
def _(mo, t):
    mo.vstack([mo.md(t("ex2_md")), mo.accordion({t("hint") + " 1": mo.md(t("ex2_h1")), t("hint") + " 2": mo.md(t("ex2_h2")), t("answer"): mo.md(t("ex2_a"))})])
    return


@app.cell
def _(np):
    def fit_line(x, y):
        """Least-squares line through the points. Returns (a, b, rms): slope, intercept, RMS error."""
        x, y = np.asarray(x, dtype=float), np.asarray(y, dtype=float)
        # (reference solution)
        xm, ym = x.mean(), y.mean()
        a = np.sum((x - xm) * (y - ym)) / np.sum((x - xm) ** 2)
        b = ym - a * xm
        rms = np.sqrt(np.mean((y - (a * x + b)) ** 2))
        return a, b, rms
    return (fit_line,)


@app.cell(hide_code=True)
def _(PULSES, READINGS, check, fit_line, mo, np, scatter_svg, t):
    ok2, _view = check(fit_line, [((PULSES, READINGS), (0.0901026, 121.56991, 0.60384), "our 21 points"),
                                  (([0, 1, 2], [1, 3, 5]), (2.0, 1.0, 0.0)),
                                  (([1, 2, 3, 4], [2, 2, 4, 4]), (0.8, 1.0, 0.44721))], tol=1e-4)
    if ok2:
        _a, _b, _rms = fit_line(PULSES, READINGS)
        _pa, _pb = np.polyfit(PULSES, READINGS, 1)
        _res = READINGS - (_a * PULSES + _b)
        _out = mo.vstack([_view, mo.md(t("fit_done").format(a=_a, b=_b, rms=_rms, pa=_pa, pb=_pb, us=1 / _a)),
                          scatter_svg(PULSES, READINGS, line=(_a, _b)), mo.md(t("resid_md")), scatter_svg(PULSES, _res, resid=True)])
    else:
        _out = _view
    _out
    return (ok2,)


@app.cell(hide_code=True)
def _(mo, t):
    mo.vstack([mo.md(t("ex3_md")), mo.accordion({t("hint") + " 1": mo.md(t("ex3_h1")), t("hint") + " 2": mo.md(t("ex3_h2")), t("answer"): mo.md(t("ex3_a"))})])
    return


@app.cell
def _():
    def us_to_ticks(us, osc):
        """PCA9685 at 50 Hz. Returns (d, n): the clock divisor and the pulse length in whole ticks."""
        # (reference solution)
        d = round(osc / (4096 * 50))
        tick_us = d / osc * 1e6
        return d, round(us / tick_us)
    return (us_to_ticks,)


@app.cell(hide_code=True)
def _(check, mo, t, us_to_ticks):
    ok3, _view = check(us_to_ticks, [((1500, 25e6), (122, 307)), ((2500, 25e6), (122, 512)), ((1500, 25.8e6), (126, 307)),
                                     ((1000, 25.8e6), (126, 205)), ((2000, 26e6), (127, 409))], tol=0)
    if ok3:
        def _real(us, told, real=25.8e6):
            d, n = us_to_ticks(us, told)
            return n * d / real * 1e6
        _rows = "\n".join(f"| {u} | {_real(u, 25e6):.1f} ({(_real(u, 25e6) / u - 1) * 100:+.2f}%) | {_real(u, 25.8e6):.1f} ({(_real(u, 25.8e6) / u - 1) * 100:+.2f}%) |"
                          for u in (1000, 1500, 2000))
        _out = mo.vstack([_view, mo.md(t("clock_md") + "\n\n" + t("clock_th") + "\n|---|---|---|\n" + _rows + "\n\n" + t("clock_after"))])
    else:
        _out = _view
    _out
    return (ok3,)


@app.cell(hide_code=True)
def _(mo, t):
    mo.vstack([mo.md(t("ex4_md")), mo.accordion({t("hint") + " 1": mo.md(t("ex4_h1")), t("hint") + " 2": mo.md(t("ex4_h2")), t("answer"): mo.md(t("ex4_a"))})])
    return


@app.cell
def _():
    FUSES = [5, 7.5, 10, 15, 20, 25, 30]   # standard blade-fuse ratings (A)

    def power_budget(i_hold, i_stall, walk_avg, cap_ah):
        """Returns (stand_A, peak_A, minutes, fuse_A) for our 18-servo robot."""
        # (reference solution)
        stand = 18 * i_hold
        peak = 6 * i_stall + 12 * i_hold
        minutes = cap_ah / walk_avg * 60
        fuse = min(f for f in FUSES if f >= 1.25 * walk_avg)
        return stand, peak, minutes, fuse
    return (power_budget,)


@app.cell(hide_code=True)
def _(check, mo, power_budget, t):
    ok4, _view = check(power_budget, [((0.3, 2.8, 10, 5.2), (5.4, 20.4, 31.2, 15)), ((0.3, 2.8, 6, 5.2), (5.4, 20.4, 52.0, 7.5)),
                                      ((0.5, 3.0, 8, 4.0), (9.0, 24.0, 30.0, 10))], tol=0.01)
    mo.vstack([_view, mo.md(t("power_after")) if ok4 else mo.md("")])
    return (ok4,)


@app.cell(hide_code=True)
def _(mo, t):
    amp = mo.ui.slider(10, 80, value=60, step=5, label=t("amp"), show_value=True)
    period = mo.ui.slider(0.6, 6, value=3, step=0.2, label=t("period"), show_value=True)
    mo.vstack([mo.md(t("r1_md")), mo.hstack([amp, period], wrap=True)])
    return amp, period


@app.cell(hide_code=True)
def _(K, amp, angle_to_pulse, json, mo, np, ok1, ok2, ok3, ok4, period, t):
    def _simulate(A, P, fps=50, dead_us=8, w_max=200):
        n = int(round(2 * P * fps))
        tt = np.arange(n) / fps
        cmd = A * np.sin(2 * np.pi * tt / P)
        us = np.array([round(float(angle_to_pulse(c, 1500, 1))) for c in cmd])
        aim_us, act, out = us[0], K * (us[0] - 1500), []
        for u in us:
            if abs(u - aim_us) > dead_us:          # deadband: ignore changes of 8 µs or less
                aim_us = u
            goal = K * (aim_us - 1500)
            act += float(np.clip(goal - act, -w_max / fps, w_max / fps))   # speed limit
            out.append(act)
        return tt, cmd, us, np.array(out)

    def _horn(cmd, act, fps):
        data = json.dumps({"c": np.round(cmd, 2).tolist(), "a": np.round(act, 2).tolist(), "fps": fps})
        return mo.iframe("""<!doctype html><html><head><meta charset='utf-8'><style>
        :root{--ink:#16202a;--muted:#5b6875;--acc:#d9771f;--bl:#2a6fb0;--bg:#fff}
        @media (prefers-color-scheme: dark){:root{--ink:#e3e9ef;--muted:#98a5b2;--acc:#f0954a;--bl:#6aa6e0;--bg:#17202a}}
        html,body{margin:0;background:var(--bg);font:12px monospace;color:var(--muted)}canvas{width:100%;height:100vh;display:block}</style></head>
        <body><canvas id='c'></canvas><script>const D=""" + data + """;
        const cv=document.getElementById('c'),x=cv.getContext('2d'),cs=n=>getComputedStyle(document.documentElement).getPropertyValue(n).trim();
        function fit(){const r=cv.getBoundingClientRect();cv.width=r.width*devicePixelRatio;cv.height=r.height*devicePixelRatio}fit();addEventListener('resize',fit);
        const t0=performance.now();
        function f(now){const k=Math.max(0,Math.floor((now-t0)/1000*D.fps))%D.c.length,W=cv.width,H=cv.height,R=Math.min(W*0.4,H*0.8),cx=W/2,cy=H*0.9,d=devicePixelRatio;
          x.clearRect(0,0,W,H);x.strokeStyle=cs('--muted');x.lineWidth=d;x.beginPath();x.arc(cx,cy,R,Math.PI,2*Math.PI);x.stroke();
          x.fillStyle=cs('--muted');x.font=(11*d)+'px monospace';x.textAlign='center';
          for(let a=-90;a<=90;a+=30){const r=(90-a)*Math.PI/180;x.beginPath();x.moveTo(cx+R*Math.cos(r),cy-R*Math.sin(r));x.lineTo(cx+(R-8*d)*Math.cos(r),cy-(R-8*d)*Math.sin(r));x.stroke();x.fillText(a+'°',cx+(R+14*d)*Math.cos(r),cy-(R+14*d)*Math.sin(r)+4*d)}
          const nd=(a,c,w,dash)=>{const r=(90-a)*Math.PI/180;x.strokeStyle=c;x.lineWidth=w*d;x.setLineDash(dash.map(v=>v*d));x.beginPath();x.moveTo(cx,cy);x.lineTo(cx+R*0.92*Math.cos(r),cy-R*0.92*Math.sin(r));x.stroke();x.setLineDash([])};
          nd(D.a[k],cs('--acc'),7,[]);nd(D.c[k],cs('--bl'),2.5,[6,5]);x.fillStyle=cs('--ink');x.beginPath();x.arc(cx,cy,6*d,0,7);x.fill();
          x.textAlign='left';x.fillStyle=cs('--muted');x.fillText('asked '+D.c[k].toFixed(1)+'°   actual '+D.a[k].toFixed(1)+'°',10*d,16*d);requestAnimationFrame(f)}
        requestAnimationFrame(f);</script></body></html>""", height="260px")

    def _plot(tt, cmd, act):
        W, H, l, b = 640, 200, 40, 24
        X = lambda v: l + v / tt[-1] * (W - l - 10)
        Y = lambda v: (H - b) / 2 - v * (H - b - 16) / 180
        path = lambda ys: "M" + " L".join(f"{X(a):.1f},{Y(c):.1f}" for a, c in zip(tt, ys))
        g = "".join(f"<line x1='{l}' y1='{Y(v):.1f}' x2='{W - 10}' y2='{Y(v):.1f}' stroke='#8883'/><text x='{l - 4}' y='{Y(v) + 4:.1f}' text-anchor='end' fill='currentColor'>{v}°</text>" for v in (-90, -45, 0, 45, 90))
        return mo.Html(f"<svg viewBox='0 0 {W} {H}' style='width:100%;max-width:640px;font:11px monospace'>{g}"
                       f"<path d='{path(act)}' fill='none' stroke='#d9771f' stroke-width='3'/>"
                       f"<path d='{path(cmd)}' fill='none' stroke='#2a6fb0' stroke-width='1.6' stroke-dasharray='5 4'/>"
                       f"<text x='{W - 10}' y='{H - 6}' text-anchor='end' fill='currentColor'>t = {tt[-1]:.1f} s</text></svg>")

    if not (ok1 and ok2 and ok3 and ok4):
        sweep = None
        _out = mo.callout(mo.md("🔒 " + t("r_locked")), kind="neutral")
    else:
        _tt, _cmd, _us, _act = _simulate(amp.value, period.value)
        sweep = (_tt, _cmd, _us)
        _lag = float(np.max(np.abs(_cmd - _act)[len(_tt) // 2:]))
        _peak = 2 * np.pi * amp.value / period.value
        _msg = t("r1_done").format(lag=_lag, peak=_peak) + ("  \n" + t("r1_fast") if _peak > 200 else "")
        _out = mo.vstack([_horn(_cmd, _act, 50), _plot(_tt, _cmd, _act), mo.callout(mo.md(_msg), kind="success" if _peak <= 200 else "warn")])
    _out
    return (sweep,)


@app.cell(hide_code=True)
def _(mo, sweep, t):
    if sweep is None:
        _out = mo.md(t("r2_md"))
    else:
        _csv = "t_s,angle_deg,pulse_us\n" + "\n".join(f"{a:.2f},{c:.2f},{u}" for a, c, u in zip(*sweep))
        _out = mo.vstack([mo.md(t("r2_md")), mo.download(data=_csv.encode(), filename="sweep.csv", label=t("r2_dl"))])
    _out
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
            "crumb": 'Stage 0 · Servos and power · practice',
            "intro": """# Turn measurements into functions ⚙️
    
    On the Stage 0 page we measured one servo: how the angle follows the pulse, how fine a step can be, how fast it turns, and how much current it draws. Here you turn those measurements into **4 small Python functions**. Every later stage calls them, so it's worth getting them exactly right.
    
    How to work: edit the code cells marked ✏️, then run them (Ctrl/Cmd + Enter). The checker under each one updates on its own and shows every test. If you're stuck, open the hints one at a time; the last one is the full answer. Pass all four to unlock a simulated servo that follows **your** pulses.""",
            "given_md": """## What you're given
    
    Three words first, because every function below uses them:
    
    - **Pulse width** (written `us`, in microseconds, µs; 1 µs = one millionth of a second): how long each control pulse stays high. This is the only thing we ever send to a servo.
    - **Joint angle θ** (theta, in degrees): where we want the horn, measured from the joint's own zero.
    - **Slope K = 0.0901 °/µs**: how many degrees the horn turns when the pulse gets 1 µs longer. We measured it on the Stage 0 page; you'll measure it again yourself in checkpoint 2.
    
    The table `DATA` holds our 21 measurements: we sent pulses from 500 to 2500 µs in steps of 100 and read the horn on a printed protractor each time. Run the cell; the plot below shows them.""",
            "data_cap": "Our 21 measurements. Horizontal: pulse width (µs). Vertical: protractor reading (°). The protractor's 0° sat at an arbitrary place, so only the **slope** of these points matters, not their height.",
            "ex1_md": """## ✏️ 1 · Pulse ↔ angle
    
    On the page we wrote the servo's line around the pulse that puts the joint at its zero:
    
    **θ = s · K · (us − us0)**
    
    Every symbol, once more:
    - `us`: the pulse we send (µs). `us0`: the pulse at which this joint sits at θ = 0. We find it for every joint in Stage 2.
    - `us − us0`: how far the pulse is from that zero pulse. Positive means longer.
    - `K`: degrees per µs (0.0901).
    - `s`: the direction sign, **+1 or −1**. Mirrored legs have servos mounted the other way round, so a longer pulse turns them the negative way; for those s = −1.
    
    Write `pulse_to_angle(us, us0, s)` straight from the formula. Then write `angle_to_pulse(theta, us0, s)`, which answers the opposite question: which pulse gives this angle? Solve the formula for `us` by hand first.""",
            "ex1_h1": '`pulse_to_angle` is the formula as written. For `angle_to_pulse`: divide both sides by s · K, then add us0 to both sides.',
            "ex1_h2": 'You should get us = us0 + θ / (s · K). Check one case by hand: θ = 10°, us0 = 1570, s = +1 gives 1570 + 111 = 1681 µs. Since s is +1 or −1, dividing by s is the same as multiplying by s.',
            "ex1_a": """```python
    def pulse_to_angle(us, us0, s):
        return s * K * (us - us0)
    
    def angle_to_pulse(theta, us0, s):
        return us0 + theta / (s * K)
    ```""",
            "ex2_md": """## ✏️ 2 · Fit the line yourself
    
    Where did K come from? From a **least-squares fit** through our 21 points. Here is what that means, one piece at a time.
    
    - We have n points (xᵢ, yᵢ), i = 1 … n. Here x is the pulse and y the protractor reading. The little i just numbers the points.
    - We look for a line **y = a·x + b**: a is the slope (how much y grows when x grows by 1), b the intercept (y at x = 0).
    - Point i misses the line by its **residual** eᵢ = yᵢ − (a·xᵢ + b): positive if the point is above the line.
    - We pick a and b to make the **sum of squared residuals** E = Σ eᵢ² as small as possible (Σ, capital sigma, means "add up over all i"). Squaring makes misses above and below count alike, and big misses count more.
    - The **mean** x̄ ("x bar") is the average, (x₁ + … + xₙ) / n; the same for ȳ.
    
    E is a smooth bowl in a and b. At its lowest point it is flat in both directions, so both partial derivatives are zero: ∂E/∂b = 0 and ∂E/∂a = 0 (a partial derivative changes one variable and holds the other still). Working these two equations out gives
    
    **b = ȳ − a · x̄  and  a = Σ (xᵢ − x̄)(yᵢ − ȳ) / Σ (xᵢ − x̄)²**
    
    Finally, the **RMS error** (root mean square) = √(mean of eᵢ²) is the typical size of a miss, in the units of y.
    
    Write `fit_line(x, y)` that returns `(a, b, rms)`. Use plain numpy sums and means, not `np.polyfit`: the checker compares your answer with polyfit afterwards.""",
            "ex2_h1": '`x.mean()` is x̄. `(x - xm)` subtracts the mean from every element at once, and `np.sum(...)` adds them up. Compute a first, then b, then the residuals.',
            "ex2_h2": 'Where does b = ȳ − a·x̄ come from? ∂E/∂b = −2 Σ (yᵢ − a·xᵢ − b) = 0 means Σyᵢ = a·Σxᵢ + n·b; divide by n. So the best line always passes through the point (x̄, ȳ). Put that b into ∂E/∂a = 0 and the formula for a drops out.',
            "ex2_a": """```python
    xm, ym = x.mean(), y.mean()
    a = np.sum((x - xm) * (y - ym)) / np.sum((x - xm) ** 2)
    b = ym - a * xm
    rms = np.sqrt(np.mean((y - (a * x + b)) ** 2))
    return a, b, rms
    ```""",
            "fit_done": 'Your fit: **a = {a:.5f} °/µs** (that is {us:.1f} µs per degree), b = {b:.2f}°, RMS = **{rms:.2f}°**. `np.polyfit` says a = {pa:.5f}, b = {pb:.2f}: the same. The orange line is your fit.',
            "resid_md": 'And the residuals, one bar per point (the orange line is zero). They stay within about ±1.3°. There is a gentle wave (above the line at both ends, below it around 1800–2100 µs), but it is about as big as the error of reading a protractor by eye, so a straight line is good enough for this servo.',
            "ex3_md": """## ✏️ 3 · From µs to ticks
    
    On the robot the pulses come from a PCA9685 chip, which can only count. The words you need:
    
    - **Oscillator frequency `osc`** (in hertz, Hz = beats per second): the chip's internal clock, nominally 25 000 000 Hz (25 MHz).
    - **Counter**: a 12-bit number that goes 0, 1, …, 4095, then wraps to 0. One step of the counter is a **tick**. A pulse starts at tick 0 and ends at a tick number we choose, so its length is a **whole number of ticks**, n.
    - **Divisor d**: the chip slows its clock down by a whole number d so that 4096 ticks fill exactly one 20 ms frame (50 frames per second). It wants d = osc / (4096 · 50), but d must be a whole number, so the chip **rounds** it.
    - One tick then lasts **d / osc** seconds. Multiply by 1 000 000 to get µs.
    
    Write `us_to_ticks(us, osc)` that returns `(d, n)`: the divisor, and the number of ticks closest to the pulse you asked for.""",
            "ex3_h1": 'Three lines: d = round(osc / (4096 · 50)); the tick length in µs = d / osc × 10⁶; n = round(us / tick).',
            "ex3_h2": "At 25 MHz you should get d = 122 and a tick of 4.88 µs, so 1500 µs is 307 ticks. Python's `round()` returns a whole number, which is what we want for both d and n.",
            "ex3_a": """```python
    d = round(osc / (4096 * 50))
    tick_us = d / osc * 1e6
    return d, round(us / tick_us)
    ```""",
            "clock_md": """### Now use it on our left board
    
    Its real clock is 25.8 MHz, not 25. The chip doesn't know; it just runs **n · d** clock beats per pulse. So the real pulse lasts n · d / 25.8 MHz. Two cases, both computed with **your** `us_to_ticks`:
    - the library is told 25 MHz (the default), so it picks d and n for the wrong clock;
    - the library is told the truth, 25.8 MHz.""",
            "clock_th": '| asked (µs) | told 25 MHz: real µs | told 25.8 MHz: real µs |',
            "clock_after": "Told the wrong clock, every pulse comes out about 3% short: at 1500 µs that is 48 µs, about 4° of joint angle. Told the truth, what is left is under half a tick. That's the one-line fix from the page.",
            "ex4_md": """## ✏️ 4 · A power budget
    
    Current I is measured in amperes (A). All 18 servos hang on the same two battery wires, so the battery wire carries the **sum** of their currents. Our model, with the numbers from the page:
    
    - **Standing**: every servo holds its joint and draws about `i_hold` (0.3 A).
    - **Peak**: the worst moment we planned for: all six femurs push close to their **stall current** `i_stall` (2.8 A; "stall" = powered but held still) at the same instant, for example when the robot stands up, while the other 12 servos hold.
    - **Run time**: a pack of capacity `cap_ah` amp-hours (Ah) lasts cap_ah / I hours at a steady current I. We use the walking average `walk_avg`. Return it in **minutes**.
    - **Fuse**: a fuse is a thin wire that melts when the current stays too high for too long. Pick the smallest rating in `FUSES` that is at least **1.25 × walk_avg**, so normal walking never blows it. A fuse reacts to heat, which builds up slowly, so a peak that lasts a fraction of a second passes through.
    
    Write `power_budget(i_hold, i_stall, walk_avg, cap_ah)` that returns `(stand_A, peak_A, minutes, fuse_A)`.""",
            "ex4_h1": 'Standing: 18 servos × i_hold. Peak: 6 × i_stall plus the other 12 × i_hold. Minutes: cap_ah / walk_avg × 60.',
            "ex4_h2": 'For the fuse, go through FUSES in order and keep the first one that is ≥ 1.25 × walk_avg. In one line: `min(f for f in FUSES if f >= 1.25 * walk_avg)`.',
            "ex4_a": """```python
    stand = 18 * i_hold
    peak = 6 * i_stall + 12 * i_hold
    minutes = cap_ah / walk_avg * 60
    fuse = min(f for f in FUSES if f >= 1.25 * walk_avg)
    return stand, peak, minutes, fuse
    ```""",
            "power_after": "With our numbers: 5.4 A standing, a 20 A peak, and about half an hour of walking from 5.2 Ah. 15 A is exactly the fuse the page recommends for the plus wire. Compare with the bench supply's 3 A limit: it can't even hold the robot standing, which is why we only use it with the feet in the air.",
            "amp": 'sweep amplitude (°)',
            "period": 'sweep period (s)',
            "r1_md": """## ★ Reward · A servo that follows your pulses
    
    The command is a slow sweep, θ(t) = A · sin(2π t / P): A is the amplitude (the biggest angle), P the period (seconds for one full swing there and back). Fifty times a second your `angle_to_pulse` turns θ into a pulse, rounded to whole µs. A simulated servo then reacts the way ours did on the page: it ignores changes of 8 µs or less (the deadband), and it turns at most 200°/s (its top speed).
    
    Dashed blue: the angle you asked for. Thick orange: where the horn really is. Try a short period with a big amplitude.""",
            "r1_done": "Worst gap between asked and actual (after the first swing): **{lag:.1f}°**. The sweep's fastest moment asks for {peak:.0f}°/s.",
            "r1_fast": "That's more than the servo's 200°/s, so the horn falls behind and the tops of the wave get cut off. This is why later stages check every joint's speed before sending anything.",
            "r2_md": """## 🤖 Bonus · Try it on a real servo
    
    Have a servo and the Arduino Nano from Stage 0? Download the sweep below (one row per 20 ms frame: time, angle, pulse), send the pulses one per frame with your Stage 0 test script, and hold a printed protractor behind the horn. With a short period you should *see* the horn fall behind, just like the orange line.""",
            "r2_dl": 'Download sweep.csv',
            "outro": """## What you just learned
    - One line, **θ = s · K · (us − us0)**, and its inverse, carry everything we know about a servo. Only us0 and s change from joint to joint.
    - **Least squares** picks the line that makes the squared misses smallest; the RMS error tells you how good the line is (0.6° here).
    - The PCA9685 can only make **whole ticks** of d / osc seconds, and it needs to know its real clock.
    - Budget power for the **peak**, not the average.
    
    **Next: Stage 1 · Forward kinematics.** Three joint angles in, one foot position out.""",
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
            "crumb": '阶段 0 · 舵机与电源 · 练习',
            "intro": """# 把测量结果变成函数 ⚙️
    
    在阶段 0 的页面上，我们测了一个舵机：角度怎样跟着脉宽走，最小能动多细，转得多快，吃多少电流。这里你要把这些测量写成 **4 个小 Python 函数**。后面每个阶段都会调用它们，所以值得一次写对。
    
    怎么做：修改标了 ✏️ 的代码格子，然后运行（Ctrl/Cmd + Enter）。每个格子下面的检查器会自动更新，列出每个测试。卡住了就一条一条展开提示，最后一条是完整答案。四个全部通过后，解锁一个跟着**你的**脉宽转动的模拟舵机。""",
            "given_md": """## 已经给你的东西
    
    先说三个词，下面每个函数都会用到：
    
    - **脉宽**（代码里写作 `us`，单位微秒 µs；1 µs = 百万分之一秒）：每个控制脉冲保持高电平的时长。我们发给舵机的永远只有这一个量。
    - **关节角 θ**（theta，单位度）：我们希望舵盘到达的位置，从这个关节自己的零位量起。
    - **斜率 K = 0.0901 °/µs**：脉宽每加长 1 µs，舵盘转多少度。我们在阶段 0 页面上测过；在检查点 2 你会自己再算一遍。
    
    表 `DATA` 是我们的 21 次测量：从 500 到 2500 µs，每隔 100 µs 发一次脉宽，每次在打印的量角器上读舵盘角度。运行这个格子，下图就是这些点。""",
            "data_cap": '我们的 21 次测量。横轴：脉宽（µs）。纵轴：量角器读数（°）。量角器的 0° 放在哪里是随意的，所以只有这些点的**斜率**有意义，它们的高低没有意义。',
            "ex1_md": """## ✏️ 1 · 脉宽 ↔ 角度
    
    页面上我们把舵机的直线写成围绕"让关节处于零位的脉宽"的形式：
    
    **θ = s · K · (us − us0)**
    
    再逐个过一遍符号：
    - `us`：我们发出的脉宽（µs）。`us0`：让这个关节处于 θ = 0 的脉宽，阶段 2 会为每个关节找出来。
    - `us − us0`：脉宽离这个零位脉宽有多远，正数表示更长。
    - `K`：每 µs 对应的度数（0.0901）。
    - `s`：方向符号，**+1 或 −1**。镜像的腿上舵机是反着装的，脉宽变长时它们往负方向转，对这些关节 s = −1。
    
    照公式写出 `pulse_to_angle(us, us0, s)`。然后写 `angle_to_pulse(theta, us0, s)`，它回答反过来的问题：要得到这个角度，该发多宽的脉冲？先在纸上把公式解出 `us`。""",
            "ex1_h1": '`pulse_to_angle` 就是原公式。`angle_to_pulse`：两边同除以 s · K，再两边同加 us0。',
            "ex1_h2": '你应该得到 us = us0 + θ / (s · K)。手算验证一例：θ = 10°，us0 = 1570，s = +1，得 1570 + 111 = 1681 µs。因为 s 只取 +1 或 −1，除以 s 和乘以 s 是一回事。',
            "ex1_a": """```python
    def pulse_to_angle(us, us0, s):
        return s * K * (us - us0)
    
    def angle_to_pulse(theta, us0, s):
        return us0 + theta / (s * K)
    ```""",
            "ex2_md": """## ✏️ 2 · 自己拟合这条直线
    
    K 是怎么来的？是对 21 个点做**最小二乘拟合**（least squares）得到的。下面一块一块说清楚它的意思。
    
    - 我们有 n 个点 (xᵢ, yᵢ)，i = 1 … n。这里 x 是脉宽，y 是量角器读数。下标 i 只是给点编号。
    - 我们要找一条直线 **y = a·x + b**：a 是斜率（x 增加 1 时 y 增加多少），b 是截距（x = 0 时的 y）。
    - 第 i 个点偏离直线的量叫**残差**（residual）eᵢ = yᵢ − (a·xᵢ + b)：点在直线上方时为正。
    - 我们选 a 和 b，使**残差平方和** E = Σ eᵢ² 尽量小（Σ 是大写 sigma，意思是"对所有 i 求和"）。平方让上下两边的偏差同等对待，并且偏得越多罚得越重。
    - **均值** x̄（读作 "x bar"）就是平均数 (x₁ + … + xₙ) / n；ȳ 同理。
    
    E 是关于 a 和 b 的一个光滑的"碗"。碗底在两个方向上都是平的，所以两个偏导数都为零：∂E/∂b = 0，∂E/∂a = 0（偏导数就是只变一个变量、另一个固定时的导数）。把这两个方程解出来得到
    
    **b = ȳ − a · x̄，  a = Σ (xᵢ − x̄)(yᵢ − ȳ) / Σ (xᵢ − x̄)²**
    
    最后，**RMS 误差**（root mean square，均方根）= √(eᵢ² 的平均值)，是一个点典型的偏差大小，单位和 y 相同。
    
    写 `fit_line(x, y)`，返回 `(a, b, rms)`。只用 numpy 的求和与均值，不要用 `np.polyfit`：检查器之后会拿你的结果和 polyfit 对比。""",
            "ex2_h1": '`x.mean()` 就是 x̄。`(x - xm)` 一次性让每个元素减去均值，`np.sum(...)` 把它们加起来。先算 a，再算 b，最后算残差。',
            "ex2_h2": 'b = ȳ − a·x̄ 从哪来？∂E/∂b = −2 Σ (yᵢ − a·xᵢ − b) = 0，即 Σyᵢ = a·Σxᵢ + n·b，两边除以 n 即得。所以最优直线一定经过点 (x̄, ȳ)。把这个 b 代入 ∂E/∂a = 0，a 的公式就出来了。',
            "ex2_a": """```python
    xm, ym = x.mean(), y.mean()
    a = np.sum((x - xm) * (y - ym)) / np.sum((x - xm) ** 2)
    b = ym - a * xm
    rms = np.sqrt(np.mean((y - (a * x + b)) ** 2))
    return a, b, rms
    ```""",
            "fit_done": '你的拟合：**a = {a:.5f} °/µs**（即每度 {us:.1f} µs），b = {b:.2f}°，RMS = **{rms:.2f}°**。`np.polyfit` 给出 a = {pa:.5f}，b = {pb:.2f}：完全一致。橙色直线就是你的拟合。',
            "resid_md": '再看残差，每个点一根竖线（橙线是零）。它们都在约 ±1.3° 以内。能看出一点轻微的起伏（两端在直线上方，1800–2100 µs 附近在下方），但幅度和用眼睛读量角器的误差差不多，所以对这个舵机来说直线已经够用。',
            "ex3_md": """## ✏️ 3 · 从 µs 到 tick
    
    在机器人上，脉冲由 PCA9685 芯片产生，而它只会数数。需要的几个词：
    
    - **振荡器频率 `osc`**（单位赫兹 Hz = 每秒节拍数）：芯片内部的时钟，标称 25 000 000 Hz（25 MHz）。
    - **计数器**：一个 12 位的数，0、1、…、4095，然后回到 0。计数器走一步叫一个 **tick**。脉冲从第 0 个 tick 开始，到我们指定的 tick 结束，所以脉宽一定是**整数个 tick**，记作 n。
    - **分频数 d**：芯片把时钟放慢 d 倍（d 是整数），让 4096 个 tick 正好填满一个 20 ms 的帧（每秒 50 帧）。理想值是 d = osc / (4096 · 50)，但 d 必须是整数，所以芯片会**四舍五入**。
    - 于是一个 tick 持续 **d / osc** 秒，乘以 1 000 000 得到 µs。
    
    写 `us_to_ticks(us, osc)`，返回 `(d, n)`：分频数，以及最接近你要的脉宽的 tick 数。""",
            "ex3_h1": '三行：d = round(osc / (4096 · 50))；tick 长度（µs）= d / osc × 10⁶；n = round(us / tick)。',
            "ex3_h2": '在 25 MHz 下你应该得到 d = 122，一个 tick 4.88 µs，所以 1500 µs 是 307 个 tick。Python 的 `round()` 返回整数，d 和 n 正需要整数。',
            "ex3_a": """```python
    d = round(osc / (4096 * 50))
    tick_us = d / osc * 1e6
    return d, round(us / tick_us)
    ```""",
            "clock_md": """### 用到我们的左板上
    
    它的真实时钟是 25.8 MHz，不是 25。芯片自己并不知道，它只管每个脉冲跑 **n · d** 个时钟节拍。所以真实脉宽是 n · d / 25.8 MHz。两种情况，都用**你的** `us_to_ticks` 计算：
    - 告诉库 25 MHz（默认值），它就按错误的时钟选 d 和 n；
    - 告诉库真实值 25.8 MHz。""",
            "clock_th": '| 要求（µs） | 告诉 25 MHz：实际 µs | 告诉 25.8 MHz：实际 µs |',
            "clock_after": '时钟告诉错了，每个脉冲都短约 3%：1500 µs 时短 48 µs，约合 4° 关节角。告诉真实值以后，剩下的误差不到半个 tick。这就是页面上那一行修正。',
            "ex4_md": """## ✏️ 4 · 电源预算
    
    电流 I 的单位是安培（A）。18 个舵机都挂在同一对电池线上，所以电池线上流的是它们电流的**总和**。我们的模型，数字都来自页面：
    
    - **站立**：每个舵机都在保持关节位置，各吃约 `i_hold`（0.3 A）。
    - **峰值**：我们按最坏时刻设计：六个 femur 同时接近**堵转电流** `i_stall`（2.8 A；"堵转" = 通电但被卡住不动），比如机器人站起来的那一下，其余 12 个舵机在保持。
    - **续航**：容量为 `cap_ah` 安时（Ah）的电池，在稳定电流 I 下能用 cap_ah / I 小时。这里用行走平均电流 `walk_avg`，结果换算成**分钟**。
    - **保险丝**：一段细金属丝，电流过大且持续够久时会熔断。在 `FUSES` 里选**不小于 1.25 × walk_avg** 的最小规格，这样正常行走永远不会把它烧断。保险丝靠发热动作，热量积累得慢，所以零点几秒的峰值能通过。
    
    写 `power_budget(i_hold, i_stall, walk_avg, cap_ah)`，返回 `(stand_A, peak_A, minutes, fuse_A)`。""",
            "ex4_h1": '站立：18 个舵机 × i_hold。峰值：6 × i_stall 加上其余 12 × i_hold。分钟：cap_ah / walk_avg × 60。',
            "ex4_h2": '保险丝：按顺序遍历 FUSES，取第一个 ≥ 1.25 × walk_avg 的。一行写法：`min(f for f in FUSES if f >= 1.25 * walk_avg)`。',
            "ex4_a": """```python
    stand = 18 * i_hold
    peak = 6 * i_stall + 12 * i_hold
    minutes = cap_ah / walk_avg * 60
    fuse = min(f for f in FUSES if f >= 1.25 * walk_avg)
    return stand, peak, minutes, fuse
    ```""",
            "power_after": '用我们的数字：站立 5.4 A，峰值 20 A，5.2 Ah 的电池大约能走半小时。15 A 正是页面建议串在正极线上的保险丝。再对比可调电源的 3 A 限流：连站着都撑不住，所以我们只在脚悬空时用它。',
            "amp": '摆动幅度（°）',
            "period": '摆动周期（s）',
            "r1_md": """## ★ 奖励 · 跟着你的脉宽转的舵机
    
    指令是一个缓慢的来回摆动 θ(t) = A · sin(2π t / P)：A 是幅度（最大角度），P 是周期（来回一整次的秒数）。每秒 50 次，你的 `angle_to_pulse` 把 θ 变成脉宽，并取整到整数 µs。模拟舵机的反应和页面上测到的一样：8 µs 以内的变化不理睬（死区），并且最快每秒转 200°（最高速度）。
    
    蓝色虚线：你要求的角度。橙色粗线：舵盘实际的位置。试试短周期配大幅度。""",
            "r1_done": '要求角度和实际角度的最大差距（第一次摆动之后）：**{lag:.1f}°**。这个摆动最快的时刻要求 {peak:.0f}°/s。',
            "r1_fast": '这超过了舵机的 200°/s，所以舵盘跟不上，波峰被削平。这就是为什么后面每个阶段在发送前都要检查每个关节的速度。',
            "r2_md": """## 🤖 附加 · 在真舵机上试试
    
    手边有舵机和阶段 0 用的 Arduino Nano？下载下面的摆动数据（每行一帧，20 ms：时间、角度、脉宽），用你阶段 0 的测试脚本每帧发一个脉宽，舵盘后面放一张打印的量角器。周期调短时，你应该能**亲眼看到**舵盘跟不上，就像那条橙线。""",
            "r2_dl": '下载 sweep.csv',
            "outro": """## 你刚学到的
    - 一条直线 **θ = s · K · (us − us0)** 和它的反函数，装下了我们对舵机的全部认识。不同关节之间只有 us0 和 s 不同。
    - **最小二乘**选出让偏差平方和最小的直线；RMS 误差说明这条线有多好（这里是 0.6°）。
    - PCA9685 只能产生**整数个 tick**，每个 tick 是 d / osc 秒，而且它需要知道自己真实的时钟。
    - 电源要按**峰值**设计，而不是平均值。
    
    **下一步：阶段 1 · 正运动学。** 输入三个关节角，输出一个脚尖位置。""",
        },
    }
    return (TEXT,)


if __name__ == "__main__":
    app.run()
