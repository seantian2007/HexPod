import marimo

__generated_with = "0.25.2"
app = marimo.App(width="medium", app_title="HexPod Academy · Stage 6 Gait")


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
    _names = ["φ, s", "path", "Walker", "frame"]
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
    # ── Given (Stages 1-5 and the Stage 6 page) — you don't need to change anything here ──
    L1, L2, L3 = 62.0, 76.0, 132.0
    LIMITS = [(-45, 45), (-75, 75), (15, 165)]
    LEGS = ["R1", "R2", "R3", "L1", "L2", "L3"]
    MOUNTS = [(85.2, -49.2, -30), (0, -98.4, -90), (-85.2, -49.2, -150),
              (85.2, 49.2, 30), (0, 98.4, 90), (-85.2, 49.2, 150)]
    HOME_FEET = np.array([[mx + 162 * np.cos(np.radians(a)), my + 162 * np.sin(np.radians(a)), -89.5]
                          for mx, my, a in MOUNTS])                 # p0: home foot positions, body frame (mm)
    GAITS = {"tripod": (1 / 2, [0, 1 / 2, 0, 1 / 2, 0, 1 / 2]),     # (beta, delta for R1 R2 R3 L1 L2 L3)
             "ripple": (2 / 3, [1 / 6, 5 / 6, 1 / 2, 2 / 3, 1 / 3, 0]),
             "wave": (5 / 6, [1 / 3, 1 / 6, 0, 5 / 6, 2 / 3, 1 / 2])}
    PERIOD = {"tripod": 2.5, "ripple": 3.0, "wave": 6.0}             # T, seconds per cycle
    H_LIFT = 30.0                                                    # swing height, mm

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

    def body_to_leg(p, i):
        """A foot position in the body frame -> the same point in leg i's frame (Stage 5, body at home)."""
        mx, my, a = MOUNTS[i]
        dx, dy = p[0] - mx, p[1] - my
        c, s = np.cos(np.radians(a)), np.sin(np.radians(a))
        return np.array([c * dx + s * dy, -s * dx + c * dy, p[2]])
    return GAITS, HOME_FEET, H_LIFT, LEGS, PERIOD, body_to_leg, ik


@app.cell(hide_code=True)
def _(mo, t):
    mo.vstack([mo.md(t("ex1_md")), mo.accordion({t("hint") + " 1": mo.md(t("ex1_h1")), t("hint") + " 2": mo.md(t("ex1_h2")), t("answer"): mo.md(t("ex1_a"))})])
    return


@app.cell
def _(GAITS):
    def leg_phase(i, t, T, gait):
        """Leg i at time t (s) in a gait with period T (s) -> (in_stance, s): True/False, and progress s in [0, 1)."""
        # (reference solution)
        beta, delta = GAITS[gait]
        phi = (t / T - delta[i]) % 1
        if phi < beta:
            return True, phi / beta
        return False, (phi - beta) / (1 - beta)
    return (leg_phase,)


@app.cell(hide_code=True)
def _(GAITS, PERIOD, check, leg_phase, mo, t):
    def _table(gait, n=24):
        """The timetable drawn from YOUR leg_phase: one row per leg, orange = stance, blue = swing."""
        T, W, rh, l = PERIOD[gait], 600, 18, 34
        out = [f"<svg viewBox='0 0 {W} {6 * rh + 22}' style='width:100%;max-width:600px;font:11px monospace'>"]
        for i, leg in enumerate(["R1", "R2", "R3", "L1", "L2", "L3"]):
            out.append(f"<text x='0' y='{i * rh + 13}' fill='currentColor'>{leg}</text>")
            for k in range(n):
                st, _s = leg_phase(i, (k + 0.5) / n * T, T, gait)
                out.append(f"<rect x='{l + k * (W - l) / n:.1f}' y='{i * rh + 2}' width='{(W - l) / n - 1:.1f}' height='{rh - 4}' rx='2' fill='{'#d9771f' if st else '#2a6fb0'}'/>")
        out.append(f"<text x='{l}' y='{6 * rh + 16}' fill='currentColor'>t = 0</text><text x='{W}' y='{6 * rh + 16}' text-anchor='end' fill='currentColor'>t = T = {T} s</text></svg>")
        return mo.Html("".join(out))

    ok1, _view = check(leg_phase, [((0, 0, 2.5, "tripod"), (True, 0.0)), ((1, 0, 2.5, "tripod"), (False, 0.0)),
                                   ((0, 0.5, 2.5, "tripod"), (True, 0.4)), ((1, 1.0, 2.5, "tripod"), (False, 0.8)),
                                   ((2, 2.0, 3, "ripple"), (True, 0.25)), ((5, 7.3, 3, "ripple"), (True, 0.65)),
                                   ((4, 4.5, 6, "wave"), (True, 0.1)), ((3, 1.0, 6, "wave"), (True, 0.4)),
                                   ((0, 7.5, 6, "wave"), (False, 0.5))], tol=1e-6)
    _parts = [_view]
    if ok1:
        _parts += [mo.md(t("tt_md"))] + [mo.vstack([mo.md(f"**{g}** (β = {GAITS[g][0]:.3f}, T = {PERIOD[g]} s)"), _table(g)]) for g in ("tripod", "ripple", "wave")]
    mo.vstack(_parts)
    return (ok1,)


@app.cell(hide_code=True)
def _(mo, t):
    mo.vstack([mo.md(t("ex2_md")), mo.accordion({t("hint") + " 1": mo.md(t("ex2_h1")), t("hint") + " 2": mo.md(t("ex2_h2")), t("answer"): mo.md(t("ex2_a"))})])
    return


@app.cell
def _(np):
    def stance_step(p, v, w, dt):
        """A planted foot at p = (x, y, z) in the body frame, body moving at v = (vx, vy) mm/s and turning at w rad/s.
        Returns where the foot is dt seconds later, still in the body frame."""
        # (reference solution)
        x, y, z = p
        return np.array([x - (v[0] - w * y) * dt, y - (v[1] + w * x) * dt, z])

    def swing_point(lift, aep, s, z0, h):
        """The swing at progress s in [0, 1]: from `lift` (where the foot left the ground) to `aep` (x, y of the next
        touch-down), z0 = ground height, h = lift height. Returns np.array([x, y, z])."""
        # (reference solution)
        c = s - np.sin(2 * np.pi * s) / (2 * np.pi)
        x = lift[0] + c * (aep[0] - lift[0])
        y = lift[1] + c * (aep[1] - lift[1])
        z = z0 + h * (1 - np.cos(2 * np.pi * s)) / 2
        return np.array([x, y, z])
    return stance_step, swing_point


@app.cell(hide_code=True)
def _(check, mo, np, stance_step, swing_point, t, verdict):
    _okS, _vS = check(stance_step, [(((100, 50, -89.5), (30, 0), 0, 0.02), (99.4, 50, -89.5), "straight, 30 mm/s"),
                                    (((100, 50, -89.5), (30, 10), 0.2, 0.02), (99.6, 49.4, -89.5), "30 / 10 mm/s, turning 0.2 rad/s"),
                                    (((0, 200, -89.5), (0, 0), 0.5, 0.1), (10, 200, -89.5), "turning on the spot")], tol=1e-6)
    _L, _A = (200, -120, -89.5), (240, -100)
    _okW, _vW = check(swing_point, [((_L, _A, 0, -89.5, 30), (200, -120, -89.5), "s = 0: lift-off"),
                                    ((_L, _A, 0.25, -89.5, 30), (203.6338, -118.1831, -74.5), "s = 0.25"),
                                    ((_L, _A, 0.5, -89.5, 30), (220, -110, -59.5), "s = 0.5: top"),
                                    ((_L, _A, 1, -89.5, 30), (240, -100, -89.5), "s = 1: touch-down")], tol=1e-3)

    def _smooth():
        try:
            _s = np.linspace(0, 1, 401)
            _P = np.array([swing_point(_L, _A, v, -89.5, 30) for v in _s])
        except Exception:
            return False, mo.md("")
        _step = np.linalg.norm(np.diff(_P, axis=0), axis=1)
        _h = 1e-5
        _v0 = float(np.linalg.norm(swing_point(_L, _A, _h, -89.5, 30) - swing_point(_L, _A, 0, -89.5, 30))) / _h
        _v1 = float(np.linalg.norm(swing_point(_L, _A, 1, -89.5, 30) - swing_point(_L, _A, 1 - _h, -89.5, 30))) / _h
        _ok = _step.max() < 0.5 and _v0 < 0.05 and _v1 < 0.05
        return _ok, verdict(_ok, [("✅ " if _ok else "❌ ") + t("smooth").format(j=_step.max(), a=_v0, b=_v1)])

    if _okW:
        _okM, _vM = _smooth()
    else:
        _okM, _vM = False, mo.md("")
    ok2 = _okS and _okW and _okM
    mo.vstack([mo.md("`stance_step`"), _vS, mo.md("`swing_point`"), _vW, _vM])
    return (ok2,)


@app.cell(hide_code=True)
def _(mo, t):
    mo.vstack([mo.md(t("ex3_md")), mo.accordion({t("hint") + " 1": mo.md(t("ex3_h1")), t("hint") + " 2": mo.md(t("ex3_h2")), t("answer"): mo.md(t("ex3_a"))})])
    return


@app.cell
def _(GAITS, HOME_FEET, H_LIFT, PERIOD, leg_phase, np, stance_step, swing_point):
    class Walker:
        def __init__(self, gait="tripod"):
            self.gait = gait
            self.beta = GAITS[gait][0]
            self.T = PERIOD[gait]
            self.t = 0.0                          # gait clock (s)
            self.p0 = HOME_FEET.copy()            # home foot positions, body frame
            self.p = HOME_FEET.copy()             # where each foot is now
            self.lift = HOME_FEET.copy()          # where each foot last left the ground
            self.was_stance = [True] * 6          # was each leg in stance on the previous step?

        def step(self, vx, vy, w, dt):
            """Advance every foot by dt for body velocity (vx, vy) mm/s and turn rate w rad/s. Returns self.p."""
            # (reference solution)
            k = self.beta * self.T / 2                       # half a stance, in seconds
            for i in range(6):
                stance, s = leg_phase(i, self.t, self.T, self.gait)
                x0, y0, z0 = self.p0[i]
                if stance:
                    self.p[i] = stance_step(self.p[i], (vx, vy), w, dt)
                    self.p[i][2] = z0                           # on the ground
                else:
                    if self.was_stance[i]:                      # it just lifted off: remember where
                        self.lift[i] = self.p[i].copy()
                    aep = (x0 + k * (vx - w * y0), y0 + k * (vy + w * x0))
                    self.p[i] = swing_point(self.lift[i], aep, s, z0, H_LIFT)
                self.was_stance[i] = stance
            self.t += dt
            return self.p
    return (Walker,)


@app.cell(hide_code=True)
def _(Walker, leg_phase, mo, np, t, verdict):
    def _run():
        try:
            w = Walker("tripod")
            if w.step(0, 0, 0, 0.02) is None:
                return False, mo.callout(mo.md("✏️ " + t("not_started")), kind="neutral")
            w = Walker("tripod")
            B, yaw, v, om, dt = np.zeros(2), 0.0, (30, 10), 0.1, 0.02
            anchor, drift, lands = [None] * 6, 0.0, []
            for _ in range(int(2 * w.T / dt)):
                was = list(w.was_stance)
                feet = np.array(w.step(v[0], v[1], om, dt), dtype=float)
                c, s = np.cos(yaw), np.sin(yaw)
                B = B + np.array([c * v[0] - s * v[1], s * v[0] + c * v[1]]) * dt
                yaw += om * dt
                c, s = np.cos(yaw), np.sin(yaw)
                for i in range(6):
                    st, _ = leg_phase(i, w.t - dt, w.T, w.gait)
                    if st:
                        W = B + np.array([c * feet[i, 0] - s * feet[i, 1], s * feet[i, 0] + c * feet[i, 1]])
                        if anchor[i] is None or not was[i]:
                            anchor[i] = W
                            lands.append(abs(feet[i, 2] + 89.5))
                        drift = max(drift, float(np.linalg.norm(W - anchor[i])))
                    else:
                        anchor[i] = None
            w0 = Walker("tripod")
            for _ in range(int(w0.T / 0.02) + 1):
                feet0 = np.array(w0.step(0, 0, 0, 0.02), dtype=float)
            home = float(np.max(np.abs(feet0 - w0.p0)))
        except Exception as e:
            return False, verdict(False, [f"❌ error: {type(e).__name__}: {e}"])
        c1, c2, c3 = drift < 0.5, max(lands) < 1e-6, home < 1e-6
        _ok = c1 and c2 and c3
        return _ok, verdict(_ok, [("✅ " if _ok else "❌ ") + t("w_head"), ("✓ " if c1 else "✗ ") + t("w_drift").format(d=drift),
                                  ("✓ " if c2 else "✗ ") + t("w_land"), ("✓ " if c3 else "✗ ") + t("w_home").format(h=home)])

    ok3, _view = _run()
    _view
    return (ok3,)


@app.cell(hide_code=True)
def _(mo, t):
    mo.vstack([mo.md(t("ex4_md")), mo.accordion({t("hint") + " 1": mo.md(t("ex4_h1")), t("hint") + " 2": mo.md(t("ex4_h2")), t("answer"): mo.md(t("ex4_a"))})])
    return


@app.cell
def _(LEGS, body_to_leg, ik, np):
    def solve_frame(feet, prev, cap=100, dt=0.02):
        """feet: (6, 3) foot positions in the body frame; prev: the previous frame's 18 angles, or None.
        Returns (18 angles, None) or (None, a readable reason)."""
        # (reference solution)
        out = []
        for i in range(6):
            a = ik(*body_to_leg(feet[i], i))
            if a is None:
                return None, f"{LEGS[i]} can't reach ({feet[i][0]:.0f}, {feet[i][1]:.0f}, {feet[i][2]:.0f})"
            out.extend(a)
        out = np.array(out)
        if prev is not None:
            speed = np.abs(out - np.asarray(prev)) / dt
            j = int(np.argmax(speed))
            if speed[j] > cap:
                return None, f"{LEGS[j // 3]} joint {j % 3 + 1} at {speed[j]:.0f}°/s > {cap}°/s"
        return out, None
    return (solve_frame,)


@app.cell(hide_code=True)
def _(HOME_FEET, mo, np, solve_frame, t, verdict):
    def _run():
        _home = np.array([0, 30, 105] * 6, dtype=float)
        _far = HOME_FEET.copy(); _far[1] = [0, -400, -89.5]
        _jump = _home.copy(); _jump[4] = 25
        try:
            a1, r1 = solve_frame(HOME_FEET, None)
            a2, r2 = solve_frame(HOME_FEET, _home)
            a3, r3 = solve_frame(_far, None)
            a4, r4 = solve_frame(HOME_FEET, _jump)
        except Exception as e:
            return False, verdict(False, [f"❌ error: {type(e).__name__}: {e}"])
        if a1 is None and r1 is None:
            return False, mo.callout(mo.md("✏️ " + t("not_started")), kind="neutral")
        c1 = a1 is not None and np.allclose(a1, _home, atol=0.01) and r1 is None
        c2 = a2 is not None and r2 is None
        c3 = a3 is None and isinstance(r3, str) and "R2" in r3
        c4 = a4 is None and isinstance(r4, str) and "°/s" in r4
        _ok = c1 and c2 and c3 and c4
        return _ok, verdict(_ok, [("✅ " if _ok else "❌ ") + t("sf_head"), ("✓ " if c1 else "✗ ") + t("sf_1"), ("✓ " if c2 else "✗ ") + t("sf_2"),
                                  ("✓ " if c3 else "✗ ") + t("sf_3").format(r=r3), ("✓ " if c4 else "✗ ") + t("sf_4").format(r=r4)])

    ok4, _view = _run()
    _view
    return (ok4,)


@app.cell(hide_code=True)
def _(mo, t):
    mo.md(t("r1_md"))
    return


@app.cell(hide_code=True)
def _(GAITS, PERIOD, Walker, mo, np, ok1, ok2, ok3, ok4, player, solve_frame, t):
    def _mission(cap=100, dt=0.02, gait="tripod"):
        beta, T = GAITS[gait][0], PERIOD[gait]
        vmax, wmax = 0.38 * cap, np.radians(min(0.15 * cap, 21))      # our teleop's speed caps
        acc = 31 / (beta * T / 2); accw = acc * wmax / vmax             # command ramp (page, Step 7)
        w = Walker(gait)
        B, yaw, cmd, dist, turned = np.zeros(2), 0.0, [0.0, 0.0], 0.0, 0.0
        frames, poses, prints, prev, phase, hold, peak = [], [], [], None, 0, 0, 0.0
        while len(frames) < 3000 and phase < 4:
            if phase == 0:                                               # walk 300 mm, braking in time
                tv, tw = min(vmax, np.sqrt(max(0.0, 2 * acc * (300 - dist)))), 0.0
            elif phase == 2:                                             # turn 90°
                tv, tw = 0.0, min(wmax, np.sqrt(max(0.0, 2 * accw * (np.pi / 2 - turned))))
            else:                                                        # stand still for one cycle
                tv, tw = 0.0, 0.0
            cmd[0] += float(np.clip(tv - cmd[0], -acc * dt, acc * dt))
            cmd[1] += float(np.clip(tw - cmd[1], -accw * dt, accw * dt))
            was = list(w.was_stance)
            feet = np.array(w.step(cmd[0], 0, cmd[1], dt), dtype=float)
            c, s = np.cos(yaw), np.sin(yaw)
            B = B + np.array([c * cmd[0], s * cmd[0]]) * dt
            yaw += cmd[1] * dt; dist += cmd[0] * dt; turned += cmd[1] * dt
            a, why = solve_frame(feet, prev, cap, dt)
            if a is None:
                return {"fail": why, "t": len(frames) * dt}
            if prev is not None:
                peak = max(peak, float(np.max(np.abs(np.asarray(a) - prev)) / dt))
            prev = np.asarray(a, dtype=float)
            frames.append(prev); poses.append((B[0], B[1], np.degrees(yaw)))
            c, s = np.cos(yaw), np.sin(yaw)
            for i in range(6):
                if w.was_stance[i] and not was[i]:                      # this foot just touched down: footprint
                    prints.append([B[0] + c * feet[i, 0] - s * feet[i, 1], B[1] + s * feet[i, 0] + c * feet[i, 1], len(frames) - 1])
            if phase in (0, 2) and cmd[0] < 0.05 and cmd[1] < 1e-3 and (dist > 290 if phase == 0 else turned > np.radians(85)):
                phase, hold = phase + 1, 0
            elif phase in (1, 3):
                hold += 1
                if hold * dt >= T:
                    phase += 1
        return {"frames": frames, "poses": poses, "prints": prints, "dist": dist, "turn": np.degrees(turned), "peak": peak, "T": len(frames) * dt}

    if not (ok1 and ok2 and ok3 and ok4):
        _out = mo.callout(mo.md("🔒 " + t("r_locked")), kind="neutral")
    else:
        _r = _mission()
        if "fail" in _r:
            _out = mo.callout(mo.md(t("r1_fail").format(t=_r["t"], r=_r["fail"])), kind="danger")
        else:
            _k = range(0, len(_r["frames"]), 2)                          # play at 25 fps to keep the page light
            _cfg = {"mode": "walk", "fps": 25, "span": 760,
                    "angles": [[[round(float(v), 2) for v in _r["frames"][k][3 * i: 3 * i + 3]] for i in range(6)] for k in _k],
                    "poses": [[round(_r["poses"][k][0], 1), round(_r["poses"][k][1], 1), 0, 0, 0, round(_r["poses"][k][2], 2)] for k in _k],
                    "prints": [[round(x, 1), round(y, 1), f // 2] for x, y, f in _r["prints"]],
                    "labels": [f"t = {k * 0.02:5.2f} s   x = {_r['poses'][k][0]:5.0f} mm   yaw = {_r['poses'][k][2]:4.0f}°" for k in _k]}
            _ok = abs(_r["dist"] - 300) <= 30 and abs(_r["turn"] - 90) <= 10
            _out = mo.vstack([player(_cfg, 440), mo.callout(mo.md(t("r1_done").format(d=_r["dist"], a=_r["turn"], p=_r["peak"], T=_r["T"], n=len(_r["prints"]))),
                                                            kind="success" if _ok else "warn")])
    _out
    return


@app.cell(hide_code=True)
def _(mo, t):
    mo.md(t("robot_md"))
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
            "crumb": 'Stage 6 · Gait · practice',
            "intro": """# Walk! 🐜
    
    A gait is a timetable for six feet plus a rule for where each foot goes. You'll build a complete walker in **4 small pieces**: each leg's place in the cycle, the two halves of a foot's path (planted and swinging), the `Walker` that moves all six feet, and a safety check on every frame. Every piece is tested before anything moves.
    
    How to work: edit the code cells marked ✏️, then run them (Ctrl/Cmd + Enter). The checker under each one updates on its own. If you're stuck, open the hints one at a time; the last one is the full answer. Pass all four, and your **digital twin** walks 30 cm, stops, and turns 90° on your code.""",
            "given_md": """## What you're given
    
    Everything is in the **body frame** (Stage 5): x forward, y left, z up, origin at the body's centre. A foot position is (x, y, z) in mm.
    
    - `HOME_FEET[i]` = **p0**, foot i's home position: 162 mm straight out from its coxa, z0 = −89.5 mm.
    - `GAITS[name]` = (**β**, **δ**): β (beta) is the **duty factor**, the fraction of each cycle a foot spends on the ground; δᵢ (delta) is leg i's **phase offset**, how far its cycle is shifted, as a fraction of a cycle. Legs are in the order R1, R2, R3, L1, L2, L3.
    - `PERIOD[name]` = **T**, the seconds one full cycle takes. `H_LIFT` = how high a swinging foot rises (30 mm).
    - `ik()` from Stage 3 and `body_to_leg()` from Stage 5 (with the body at home).
    
    The velocity command is **v = (vx, vy)** in mm/s, the body's speed along its own x and y, and **w** (ω, omega) in **rad/s**, how fast the body turns about its vertical axis, positive = left.""",
            "ex1_md": """## ✏️ 1 · Where is each leg in its cycle?
    
    **The phase φ** (phi) says how far through its cycle a leg is: 0 at the start, growing to 1, then starting again. For one leg with no offset, φ = (t / T) mod 1. "mod 1" keeps only the fractional part: 2.3 mod 1 = 0.3. In Python, `x % 1` does that, and it stays in [0, 1) even for negative x.
    
    **Why the offsets δ?** If every leg used the same φ, all six would lift at once and the robot would fall. So leg i runs the same cycle, shifted: **φᵢ = (t / T − δᵢ) mod 1**. In a tripod, R1, R3, L2 have δ = 0 and R2, L1, L3 have δ = ½: when one group's cycle starts, the other's is half over.
    
    **Stance or swing?** The first fraction β of every cycle is **stance** (foot on the ground), the rest is **swing** (in the air). Within each part, the **progress s** goes from 0 to 1:
    - φ < β → stance, s = φ / β
    - φ ≥ β → swing, s = (φ − β) / (1 − β)
    
    Write `leg_phase(i, t, T, gait)` that returns `(in_stance, s)`.""",
            "ex1_h1": '`beta, delta = GAITS[gait]`, then `phi = (t / T - delta[i]) % 1`.',
            "ex1_h2": "Check one by hand: tripod, R2 (δ = ½) at t = 1.0 s, T = 2.5 s: φ = (0.4 − 0.5) mod 1 = 0.9. That's ≥ ½, so swing, s = (0.9 − 0.5) / 0.5 = 0.8.",
            "ex1_a": """```python
    beta, delta = GAITS[gait]
    phi = (t / T - delta[i]) % 1
    if phi < beta:
        return True, phi / beta
    return False, (phi - beta) / (1 - beta)
    ```""",
            "tt_md": 'Here are the three timetables, drawn by **your** `leg_phase` (orange = on the ground, blue = in the air, one full cycle from left to right). Every row is the same pattern, slid sideways by its δ. Count the orange cells in any column: 3 for tripod, 4 for ripple, 5 for wave, that is 6β.',
            "ex2_md": """## ✏️ 2 · The two halves of a foot's path
    
    **Stance: the foot stays still in the world.** But we write foot positions in the **body** frame, and the body moves. Seen from the body, a planted foot at p therefore moves the opposite way to the body: back by the body's velocity v, and around by its turning. A point at p on a body turning at ω moves at **ω × p = (−ω·py, ω·px)**: at right angles to p, with speed ω·|p| (the radian note from Stage 4). So:
    
    **dp/dt = −(v + ω × p)**, and over a short time dt: p ← p − (v + ω × p) · dt. The height stays the same.
    
    **Swing: a smooth arc from lift-off to touch-down.** The foot must travel from where it lifted (`lift`) to its next touch-down point (`aep`, the anterior extreme position) in the swing time. A straight line at constant speed would start and stop with a jolt. We use a **cycloid** instead. As s goes from 0 to 1:
    - c(s) = s − sin(2πs) / (2π) goes from 0 to 1 too, but starts and ends with zero slope (its derivative, 1 − cos 2πs, is 0 at both ends);
    - x = lift_x + c(s) · (aep_x − lift_x), and the same for y;
    - z = z0 + h · (1 − cos 2πs) / 2: up from the ground to h at s = ½ and back down.
    
    Write `stance_step(p, v, w, dt)` and `swing_point(lift, aep, s, z0, h)`. The checker also walks the swing in 400 tiny steps to make sure it has no jumps and starts and ends at zero speed.""",
            "ex2_h1": 'stance_step: unpack `x, y, z = p`; then x − (vx − w·y)·dt and y − (vy + w·x)·dt. Keep z.',
            "ex2_h2": 'swing_point: compute c first. At s = 0.5, c = 0.5 and z = z0 + h: the top of the arc, halfway across.',
            "ex2_a": """```python
    def stance_step(p, v, w, dt):
        x, y, z = p
        return np.array([x - (v[0] - w * y) * dt, y - (v[1] + w * x) * dt, z])
    
    def swing_point(lift, aep, s, z0, h):
        c = s - np.sin(2 * np.pi * s) / (2 * np.pi)
        x = lift[0] + c * (aep[0] - lift[0])
        y = lift[1] + c * (aep[1] - lift[1])
        z = z0 + h * (1 - np.cos(2 * np.pi * s)) / 2
        return np.array([x, y, z])
    ```""",
            "smooth": 'Swing in 400 steps: largest step {j:.2f} mm (no jumps); speed at lift-off {a:.3f} and at touch-down {b:.3f} mm per unit of s (zero relative to the body).',
            "ex3_md": """## ✏️ 3 · The Walker
    
    Now put it together. Each call to `step(vx, vy, w, dt)` advances all six feet by one frame. For each leg i:
    
    1. Ask `leg_phase(i, self.t, self.T, self.gait)` whether it is in stance, and its progress s.
    2. **Stance**: `self.p[i] = stance_step(self.p[i], (vx, vy), w, dt)`, then pin it to the ground, `self.p[i][2] = z0`: the last swing frame may end a hair above the floor, because s never lands exactly on 1 between two frames.
    3. **Swing**: if the leg was in stance on the previous step (`self.was_stance[i]`), it has just lifted off, so remember where: `self.lift[i] = self.p[i].copy()`. Then aim for the touch-down point. The page chose it so that the foot passes its home p0 exactly halfway through the next stance; half a stance lasts βT/2, so:
    
       **AEP = p0 + (βT / 2) · (v + ω × p0)**
    
       and set `self.p[i] = swing_point(self.lift[i], AEP, s, z0, H_LIFT)`.
    4. Remember `self.was_stance[i]` for next time.
    
    After the loop, advance the clock, `self.t += dt`, and return `self.p`.
    
    The checker drives your Walker at v = (30, 10) mm/s while turning at 0.1 rad/s for two full cycles, and follows every planted foot **in the world**. It must not move.""",
            "ex3_h1": 'The command enters the AEP formula as v + ω × p0 = (vx − w·y0, vy + w·x0), where (x0, y0, z0) = self.p0[i].',
            "ex3_h2": "Compute `k = self.beta * self.T / 2` once before the loop. With a zero command, the AEP is just p0, so after one cycle every foot is back home: that's how the robot stops.",
            "ex3_a": """```python
    k = self.beta * self.T / 2                       # half a stance, in seconds
    for i in range(6):
        stance, s = leg_phase(i, self.t, self.T, self.gait)
        x0, y0, z0 = self.p0[i]
        if stance:
            self.p[i] = stance_step(self.p[i], (vx, vy), w, dt)
            self.p[i][2] = z0                           # on the ground
        else:
            if self.was_stance[i]:                      # it just lifted off: remember where
                self.lift[i] = self.p[i].copy()
            aep = (x0 + k * (vx - w * y0), y0 + k * (vy + w * x0))
            self.p[i] = swing_point(self.lift[i], aep, s, z0, H_LIFT)
        self.was_stance[i] = stance
    self.t += dt
    return self.p
    ```""",
            "w_head": 'Walker, followed in the world',
            "w_drift": 'planted feet stayed put in the world: worst drift **{d:.2f} mm** over two cycles (the small rest is from taking finite steps dt)',
            "w_land": 'every foot touched down exactly on the ground (z = z0)',
            "w_home": 'with a zero command, all feet are home after one cycle (off by {h:.2g} mm)',
            "ex4_md": """## ✏️ 4 · Check every frame before it moves
    
    The Walker only says where the feet should be. Before a frame goes to the servos, turn it into 18 angles and refuse anything unsafe, with a reason a person can read:
    
    - **Reach**: move each foot into its leg frame with `body_to_leg(feet[i], i)` and call `ik()`. If it returns None, refuse: name the leg.
    - **Speed**: if there is a previous frame (`prev` is not None), each joint's speed is |angle − previous angle| / dt. If any is above `cap` (100°/s), refuse: name the joint and its speed, with **°/s** in the message.
    
    Write `solve_frame(feet, prev)` that returns `(angles, None)` with 18 angles, or `(None, reason)`. Our real robot runs exactly this check every 20 ms; when it refuses, the robot goes back to home instead of doing something wild.""",
            "ex4_h1": "Same structure as Stage 5's body_ik: a loop over the six legs, collecting angles with `out.extend(a)`, returning early with a reason on the first failure.",
            "ex4_h2": 'Speed: `speed = np.abs(out - np.asarray(prev)) / dt`, then `j = int(np.argmax(speed))`. Joint j is on leg `LEGS[j // 3]`.',
            "ex4_a": """```python
    out = []
    for i in range(6):
        a = ik(*body_to_leg(feet[i], i))
        if a is None:
            return None, f"{LEGS[i]} can't reach ({feet[i][0]:.0f}, {feet[i][1]:.0f}, {feet[i][2]:.0f})"
        out.extend(a)
    out = np.array(out)
    if prev is not None:
        speed = np.abs(out - np.asarray(prev)) / dt
        j = int(np.argmax(speed))
        if speed[j] > cap:
            return None, f"{LEGS[j // 3]} joint {j % 3 + 1} at {speed[j]:.0f}°/s > {cap}°/s"
    return out, None
    ```""",
            "sf_head": 'solve_frame() on four test frames',
            "sf_1": 'home feet, no previous frame → home angles',
            "sf_2": 'home feet again, previous frame = home → accepted (speed 0)',
            "sf_3": 'R2 foot 400 mm away → refused: "{r}"',
            "sf_4": 'a joint 5° away from the previous frame (250°/s) → refused: "{r}"',
            "r1_md": """## ★ Reward · Your digital twin walks
    
    The mission: walk **30 cm** straight ahead, stop, turn **90°** to the left, stop. A small script plays the gamepad: it ramps the command up and down (Step 7 of the page) at our real speed caps, 38 mm/s and 15°/s for a 100°/s joint cap. Every frame goes through **your** Walker and **your** solve_frame. Footprints stay where each foot touched down. Drag to rotate.""",
            "r1_fail": 'solve_frame() refused a frame at t = {t:.2f} s: **{r}**. The mission stops there, as the real robot would.',
            "r1_done": "**Mission complete on your code:** walked **{d:.0f} mm**, turned **{a:.1f}°**, in {T:.1f} s, {n} footprints. Busiest joint: **{p:.0f}°/s** (cap 100). The page's targets for the real robot: distance within 10%, turn within 10°.",
            "robot_md": """## 🤖 Bonus · Drive the real robot
    
    The same loop runs our robot: every 20 ms read the gamepad, step the Walker, solve the frame, check it, send it. With the robot plugged in, run our gamepad teleop from the `code/` folder: `python3 telop.py`. Then mark the floor with tape: 30 cm straight within 10% and 5° of heading, then a 90° turn within 10°. **Clear the floor and keep the USB cable slack.**
    
    **Going further.** The mission uses the tripod. Try ripple or wave in `_mission` (it's in the hidden code of the reward cell): at t = 0 some of their legs are already halfway through a swing, so the first frame jumps and solve_frame refuses it. The page's Walker fixes that with a **start hold**: legs that start mid-swing wait on the ground until their next cycle. Can you add it?""",
            "outro": """## What you just learned
    - A gait is a **timetable**: φᵢ = (t / T − δᵢ) mod 1, stance while φᵢ < β. The offsets δ spread the swings out; β decides how many feet are down (6β).
    - In the body frame a planted foot moves by **−(v + ω × p)**; a swing follows a **cycloid** that starts and ends gently.
    - The touch-down point **AEP = p0 + (βT/2)(v + ω × p0)** makes every stance pass through home, which is also how the robot stops.
    - Check **reach and joint speed on every frame** before it moves.
    
    **Next: Stage 7 · Real-time on the ESP32.** Move this loop from the laptop onto the robot.""",
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
            "crumb": '阶段 6 · 步态 · 练习',
            "intro": """# 走起来！🐜
    
    步态就是六只脚的一张时间表，再加上每只脚往哪里落的规则。你会分 **4 小块**做出一个完整的行走器：每条腿在周期中的位置，脚尖路径的两半（踩住和摆动），移动全部六只脚的 `Walker`，以及每一帧的安全检查。每一块都在任何东西动起来之前测试过。
    
    怎么做：修改标了 ✏️ 的代码格子，然后运行（Ctrl/Cmd + Enter）。每个格子下面的检查器会自动更新。卡住了就一条一条展开提示，最后一条是完整答案。四个全部通过后，你的**数字孪生**就会用你的代码走 30 cm、停下、再转 90°。""",
            "given_md": """## 已经给你的东西
    
    所有东西都在**机身坐标系**里（阶段 5）：x 向前，y 向左，z 向上，原点在机身中心。脚尖位置是 (x, y, z)，单位 mm。
    
    - `HOME_FEET[i]` = **p0**，第 i 只脚的 home 位置：从它的 coxa 笔直向外 162 mm，z0 = −89.5 mm。
    - `GAITS[name]` = (**β**, **δ**)：β（beta）是**占空比**（duty factor），每个周期中脚着地时间所占的比例；δᵢ（delta）是第 i 条腿的**相位偏移**，即它的周期被错开了多少，以周期的比例表示。腿的顺序是 R1、R2、R3、L1、L2、L3。
    - `PERIOD[name]` = **T**，一个完整周期的秒数。`H_LIFT` = 摆动的脚抬多高（30 mm）。
    - 阶段 3 的 `ik()` 和阶段 5 的 `body_to_leg()`（机身在 home）。
    
    速度指令是 **v = (vx, vy)**，单位 mm/s，即机身沿它自己的 x 和 y 方向的速度；以及 **w**（ω，omega），单位 **rad/s**，机身绕竖直轴转动的快慢，向左为正。""",
            "ex1_md": """## ✏️ 1 · 每条腿在周期的哪里？
    
    **相位 φ**（phi）表示一条腿在它的周期里走到了哪里：开始时为 0，逐渐增长到 1，然后从头再来。对一条没有偏移的腿，φ = (t / T) mod 1。"mod 1" 只保留小数部分：2.3 mod 1 = 0.3。在 Python 里 `x % 1` 就做这件事，而且即使 x 是负数，结果也在 [0, 1) 内。
    
    **为什么要偏移 δ？** 如果每条腿都用同一个 φ，六条腿会同时抬起，机器人就摔了。所以第 i 条腿跑同一个周期，只是错开：**φᵢ = (t / T − δᵢ) mod 1**。tripod 里 R1、R3、L2 的 δ = 0，R2、L1、L3 的 δ = ½：一组的周期开始时，另一组的已经过了一半。
    
    **着地还是摆动？** 每个周期的前 β 部分是**支撑相**（stance，脚在地上），其余是**摆动相**（swing，在空中）。在每一部分内，**进度 s** 从 0 走到 1：
    - φ < β → 支撑，s = φ / β
    - φ ≥ β → 摆动，s = (φ − β) / (1 − β)
    
    写 `leg_phase(i, t, T, gait)`，返回 `(in_stance, s)`。""",
            "ex1_h1": '`beta, delta = GAITS[gait]`，然后 `phi = (t / T - delta[i]) % 1`。',
            "ex1_h2": '手算一个：tripod，R2（δ = ½），t = 1.0 s，T = 2.5 s：φ = (0.4 − 0.5) mod 1 = 0.9。它 ≥ ½，所以是摆动，s = (0.9 − 0.5) / 0.5 = 0.8。',
            "ex1_a": """```python
    beta, delta = GAITS[gait]
    phi = (t / T - delta[i]) % 1
    if phi < beta:
        return True, phi / beta
    return False, (phi - beta) / (1 - beta)
    ```""",
            "tt_md": '下面是三张时间表，由**你的** `leg_phase` 画出（橙 = 着地，蓝 = 在空中，从左到右是一个完整周期）。每一行都是同一个图案，按它的 δ 横向错开。数任意一列里橙色格子的个数：tripod 3 个，ripple 4 个，wave 5 个，正好是 6β。',
            "ex2_md": """## ✏️ 2 · 脚尖路径的两半
    
    **支撑相：脚在世界系里不动。** 但我们是在**机身**坐标系里写脚的位置，而机身在动。所以从机身看，位于 p 的着地脚朝与机身相反的方向移动：随机身速度 v 向后，并随机身的转动绕圈。机身以 ω 转动时，位于 p 的点的速度是 **ω × p = (−ω·py, ω·px)**：方向垂直于 p，速率 ω·|p|（阶段 4 的弧度说明）。所以：
    
    **dp/dt = −(v + ω × p)**，在很短的时间 dt 内：p ← p − (v + ω × p) · dt。高度不变。
    
    **摆动相：从离地到落地的一段平滑弧线。** 脚要在摆动时间内，从它离地的位置（`lift`）移到下一个落地点（`aep`，anterior extreme position，前极限位置）。匀速走直线会在起止时猛地一顿。我们改用**摆线**（cycloid）。s 从 0 到 1 时：
    - c(s) = s − sin(2πs) / (2π) 也从 0 到 1，但起点和终点的斜率为零（它的导数 1 − cos 2πs 在两端都是 0）；
    - x = lift_x + c(s) · (aep_x − lift_x)，y 同理；
    - z = z0 + h · (1 − cos 2πs) / 2：从地面升到 s = ½ 时的 h，再落回去。
    
    写 `stance_step(p, v, w, dt)` 和 `swing_point(lift, aep, s, z0, h)`。检查器还会把摆动分成 400 小步走一遍，确认没有跳变，并且起止速度为零。""",
            "ex2_h1": 'stance_step：先拆开 `x, y, z = p`；然后 x − (vx − w·y)·dt 和 y − (vy + w·x)·dt。z 不变。',
            "ex2_h2": 'swing_point：先算 c。s = 0.5 时 c = 0.5，z = z0 + h：弧线最高点，正好走到一半。',
            "ex2_a": """```python
    def stance_step(p, v, w, dt):
        x, y, z = p
        return np.array([x - (v[0] - w * y) * dt, y - (v[1] + w * x) * dt, z])
    
    def swing_point(lift, aep, s, z0, h):
        c = s - np.sin(2 * np.pi * s) / (2 * np.pi)
        x = lift[0] + c * (aep[0] - lift[0])
        y = lift[1] + c * (aep[1] - lift[1])
        z = z0 + h * (1 - np.cos(2 * np.pi * s)) / 2
        return np.array([x, y, z])
    ```""",
            "smooth": '摆动分 400 步：最大一步 {j:.2f} mm（没有跳变）；离地时速度 {a:.3f}，落地时 {b:.3f} mm（每单位 s，相对机身为零）。',
            "ex3_md": """## ✏️ 3 · Walker
    
    现在把它们拼起来。每调用一次 `step(vx, vy, w, dt)`，六只脚都前进一帧。对每条腿 i：
    
    1. 用 `leg_phase(i, self.t, self.T, self.gait)` 问它是否在支撑相，以及进度 s。
    2. **支撑**：`self.p[i] = stance_step(self.p[i], (vx, vy), w, dt)`，然后把它按到地面上，`self.p[i][2] = z0`：两帧之间 s 不会正好落在 1 上，所以摆动的最后一帧可能离地面还差一丝。
    3. **摆动**：如果这条腿上一步还在支撑相（`self.was_stance[i]`），说明它刚刚离地，记住位置：`self.lift[i] = self.p[i].copy()`。然后瞄准落地点。页面上选的落地点让脚在下一个支撑相的正中间经过它的 home p0；半个支撑相持续 βT/2，所以：
    
       **AEP = p0 + (βT / 2) · (v + ω × p0)**
    
       并设 `self.p[i] = swing_point(self.lift[i], AEP, s, z0, H_LIFT)`。
    4. 记下 `self.was_stance[i]`，留给下一步用。
    
    循环结束后推进时钟 `self.t += dt`，返回 `self.p`。
    
    检查器以 v = (30, 10) mm/s、同时以 0.1 rad/s 转动来驱动你的 Walker，走两个完整周期，并在**世界系**里跟踪每一只着地的脚。它必须不动。""",
            "ex3_h1": '指令进入 AEP 公式的形式是 v + ω × p0 = (vx − w·y0, vy + w·x0)，其中 (x0, y0, z0) = self.p0[i]。',
            "ex3_h2": '在循环之前算一次 `k = self.beta * self.T / 2`。指令为零时 AEP 就是 p0，所以一个周期后每只脚都回到 home：机器人就是这样停下来的。',
            "ex3_a": """```python
    k = self.beta * self.T / 2                       # half a stance, in seconds
    for i in range(6):
        stance, s = leg_phase(i, self.t, self.T, self.gait)
        x0, y0, z0 = self.p0[i]
        if stance:
            self.p[i] = stance_step(self.p[i], (vx, vy), w, dt)
            self.p[i][2] = z0                           # on the ground
        else:
            if self.was_stance[i]:                      # it just lifted off: remember where
                self.lift[i] = self.p[i].copy()
            aep = (x0 + k * (vx - w * y0), y0 + k * (vy + w * x0))
            self.p[i] = swing_point(self.lift[i], aep, s, z0, H_LIFT)
        self.was_stance[i] = stance
    self.t += dt
    return self.p
    ```""",
            "w_head": '在世界系里跟踪 Walker',
            "w_drift": '着地的脚在世界系里没有动：两个周期内最大漂移 **{d:.2f} mm**（剩下的一点点来自有限步长 dt）',
            "w_land": '每只脚都正好落在地面上（z = z0）',
            "w_home": '指令为零时，一个周期后所有脚都回到 home（误差 {h:.2g} mm）',
            "ex4_md": """## ✏️ 4 · 每一帧动之前先检查
    
    Walker 只说脚应该在哪里。一帧送到舵机之前，要把它变成 18 个角，并拒绝任何不安全的东西，附上人看得懂的原因：
    
    - **可达性**：用 `body_to_leg(feet[i], i)` 把每只脚变到它的腿坐标系，调用 `ik()`。返回 None 就拒绝：写明是哪条腿。
    - **速度**：如果有上一帧（`prev` 不是 None），每个关节的速度是 |角度 − 上一帧角度| / dt。只要有一个超过 `cap`（100°/s）就拒绝：写明是哪个关节、速度多少，消息里要带 **°/s**。
    
    写 `solve_frame(feet, prev)`，返回 `(angles, None)`（18 个角），或者 `(None, reason)`。我们的真机器人每 20 ms 都正是做这个检查；一旦拒绝，机器人就回到 home，而不是乱动。""",
            "ex4_h1": '结构和阶段 5 的 body_ik 一样：遍历六条腿，用 `out.extend(a)` 收集角度，第一次失败就带着原因提前返回。',
            "ex4_h2": '速度：`speed = np.abs(out - np.asarray(prev)) / dt`，然后 `j = int(np.argmax(speed))`。关节 j 在 `LEGS[j // 3]` 这条腿上。',
            "ex4_a": """```python
    out = []
    for i in range(6):
        a = ik(*body_to_leg(feet[i], i))
        if a is None:
            return None, f"{LEGS[i]} can't reach ({feet[i][0]:.0f}, {feet[i][1]:.0f}, {feet[i][2]:.0f})"
        out.extend(a)
    out = np.array(out)
    if prev is not None:
        speed = np.abs(out - np.asarray(prev)) / dt
        j = int(np.argmax(speed))
        if speed[j] > cap:
            return None, f"{LEGS[j // 3]} joint {j % 3 + 1} at {speed[j]:.0f}°/s > {cap}°/s"
    return out, None
    ```""",
            "sf_head": 'solve_frame() 处理四个测试帧',
            "sf_1": 'home 脚位，没有上一帧 → home 角度',
            "sf_2": '还是 home 脚位，上一帧 = home → 接受（速度 0）',
            "sf_3": 'R2 的脚在 400 mm 外 → 拒绝："{r}"',
            "sf_4": '某个关节和上一帧差 5°（250°/s）→ 拒绝："{r}"',
            "r1_md": """## ★ 奖励 · 你的数字孪生走起来
    
    任务：笔直向前走 **30 cm**，停下，向左转 **90°**，停下。一个小脚本扮演手柄：按我们真实的速度上限（关节上限 100°/s 时为 38 mm/s 和 15°/s）把指令平滑地加上去、减下来（页面第 7 步）。每一帧都经过**你的** Walker 和**你的** solve_frame。脚印留在每只脚落地的地方。拖动可以旋转。""",
            "r1_fail": 'solve_frame() 在 t = {t:.2f} s 拒绝了一帧：**{r}**。任务在这里停下，就像真机器人那样。',
            "r1_done": '**用你的代码完成了任务：** 走了 **{d:.0f} mm**，转了 **{a:.1f}°**，用时 {T:.1f} s，{n} 个脚印。最忙的关节：**{p:.0f}°/s**（上限 100）。页面给真机定的目标：距离误差 10% 以内，转角误差 10° 以内。',
            "robot_md": """## 🤖 附加 · 驾驶真机器人
    
    我们的机器人跑的是同一个循环：每 20 ms 读手柄、推进 Walker、求解这一帧、检查、发送。插上机器人，在 `code/` 文件夹里运行我们的手柄遥控脚本：`python3 telop.py`。然后用胶带在地上做标记：直走 30 cm，距离误差 10% 以内、航向误差 5° 以内；再转 90°，误差 10° 以内。**清空地面，USB 线要留松。**
    
    **更进一步。** 任务用的是 tripod。在 `_mission` 里试试 ripple 或 wave（在奖励格子的隐藏代码里）：t = 0 时它们有几条腿已经摆到一半，所以第一帧会跳变，solve_frame 会拒绝它。页面上的 Walker 用**起步保持**（start hold）解决：一开始就处于摆动中途的腿，先在地上等到下一个周期。你能把它加上吗？""",
            "outro": """## 你刚学到的
    - 步态就是一张**时间表**：φᵢ = (t / T − δᵢ) mod 1，φᵢ < β 时着地。偏移 δ 把各条腿的摆动错开；β 决定有几只脚着地（6β）。
    - 在机身系里，着地的脚以 **−(v + ω × p)** 移动；摆动沿一条起止都很柔和的**摆线**。
    - 落地点 **AEP = p0 + (βT/2)(v + ω × p0)** 让每个支撑相都经过 home，机器人也正是这样停下来的。
    - 每一帧动之前都要检查**可达性和关节速度**。
    
    **下一步：阶段 7 · ESP32 实时架构。** 把这个循环从笔记本电脑搬到机器人上。""",
        },
    }
    return (TEXT,)


if __name__ == "__main__":
    app.run()
