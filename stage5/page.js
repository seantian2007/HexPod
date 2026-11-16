(() => {
  const $ = id => document.getElementById(id);
  const C = Site.C, t = Site.t, { seg, dot, label, arrow } = Site.cv, D = Math.PI / 180;
  const f1 = v => (Math.abs(v) < 0.05 ? 0 : v).toFixed(1);
  const vec = v => `(${f1(v[0])}, ${f1(v[1])})`;
  const R2 = (a, v) => [Math.cos(a) * v[0] - Math.sin(a) * v[1], Math.sin(a) * v[0] + Math.cos(a) * v[1]];
  const watch = (el, fn) => new IntersectionObserver(es => es.forEach(e => fn(e.isIntersecting))).observe(el);
  const FOOT = HX.FEET[0], R1 = HX.LEGS[0];                  // the front-right leg is our example everywhere
  const HEX = [0, 1, 2, 5, 4, 3].map(i => HX.LEGS[i].m);
  function poly(ctx, pts, fill, stroke, w, dash) {
    ctx.beginPath(); pts.forEach((p, j) => j ? ctx.lineTo(p[0], p[1]) : ctx.moveTo(p[0], p[1])); ctx.closePath();
    if (fill) { ctx.fillStyle = fill; ctx.fill(); }
    if (stroke) { ctx.strokeStyle = stroke; ctx.lineWidth = w || 1.5; ctx.setLineDash(dash || []); ctx.stroke(); ctx.setLineDash([]); }
  }
  // a frame's two axes: dashed on the negative side, arrow on the positive side
  function axes(ctx, P, o, ang, len, col, w, names) {     // names = null: no labels
    const ex = [Math.cos(ang), Math.sin(ang)], ey = [-Math.sin(ang), Math.cos(ang)];
    [[ex, names && names[0], true], [ey, names && names[1], false]].forEach(([e, n, isX]) => {
      seg(ctx, P([o[0] - e[0] * len * 0.55, o[1] - e[1] * len * 0.55]), P(o), col, Math.max(1, w - 1), [4, 5]);
      const tip = P([o[0] + e[0] * len, o[1] + e[1] * len]); arrow(ctx, P(o), tip, col, w);
      if (n) label(ctx, n, [tip[0] + (isX ? 8 : -6), tip[1] + (isX ? 4 : -8)], col, 14, isX ? 'left' : 'right');
    });
  }

  /* ---------- 1. one point, two frames ---------- */
  {
    const cv = $('twoF'), ctx = cv.getContext('2d'), tx = $('tx'), tp = $('tpsi');
    const s = 1.3, ox = 420, oy = 420, P = p => [ox - s * p[1], oy - s * p[0]];   // top view: x up, y left
    function draw() {
      const T = [+tx.value, 0], ps = +tp.value * D;
      ctx.clearRect(0, 0, cv.width, cv.height);
      const ex = [Math.cos(ps), Math.sin(ps)], ey = [-Math.sin(ps), Math.cos(ps)];
      poly(ctx, HEX.map(m => P(m)), null, C.line, 1.5, [5, 5]);
      poly(ctx, HEX.map(m => { const r = R2(ps, m); return P([T[0] + r[0], T[1] + r[1]]); }), C.body, C.ink, 1.5);
      axes(ctx, P, [0, 0], 0, 260, C.blue, 2.5, ['x_world', 'y_world']);
      axes(ctx, P, T, ps, 260, C.accent, 3, ['x_body', 'y_body']);
      const d = [FOOT[0] - T[0], FOOT[1] - T[1]], a = d[0] * ex[0] + d[1] * ex[1], b = d[0] * ey[0] + d[1] * ey[1];
      const F = P(FOOT), wx = [FOOT[0], 0], wy = [0, FOOT[1]];
      const pa = [T[0] + a * ex[0], T[1] + a * ex[1]], pb = [T[0] + b * ey[0], T[1] + b * ey[1]];
      seg(ctx, F, P(wx), C.blue, 1.2, [3, 4]); seg(ctx, F, P(wy), C.blue, 1.2, [3, 4]);
      seg(ctx, F, P(pa), C.accent, 1.2, [3, 4]); seg(ctx, F, P(pb), C.accent, 1.2, [3, 4]);
      [[wx, C.blue], [wy, C.blue], [pa, C.accent], [pb, C.accent]].forEach(([p, c]) => dot(ctx, P(p), 4, c));
      label(ctx, f1(FOOT[0]), [P(wx)[0] + 8, P(wx)[1] + 16], C.blue, 13);
      label(ctx, f1(FOOT[1]), [P(wy)[0], P(wy)[1] + 20], C.blue, 13, 'center');
      label(ctx, f1(a), [P(pa)[0] - 8, P(pa)[1] - 6], C.accent, 13, 'right');
      label(ctx, f1(b), [P(pb)[0] + 8, P(pb)[1] - 8], C.accent, 13);
      dot(ctx, F, 8, C.ink); label(ctx, t('twoFoot'), [F[0] + 12, F[1] - 10], C.ink, 14);
      Site.kv($('tkv'), [[t('twoInW'), `<span style="color:var(--blue)">${vec(FOOT)}</span>`], [t('twoInB'), `<span style="color:var(--accent)">${vec([a, b])}</span>`], [t('twoDist'), `${Math.hypot(a, b).toFixed(1)} mm`]]);
    }
    Site.slider(tx, v => `${v} mm`, draw); Site.slider(tp, v => `${v}°`, draw);
    Site.onLang(draw); Site.onTheme(draw); draw();
  }

  /* ---------- 2. roll, pitch, yaw ---------- */
  {
    const cv = $('rpy'), ctx = cv.getContext('2d');
    const AX = [{ k: 'roll', i: 3, amp: 12 }, { k: 'pitch', i: 4, amp: 12 }, { k: 'yaw', i: 5, amp: 16 }];
    let on = false;
    const t0 = performance.now();
    function draw() {
      const narrow = cv.clientWidth > 0 && cv.clientWidth < 620, W = narrow ? 560 : 1100, H = narrow ? 960 : 330;
      if (cv.width !== W || cv.height !== H) { cv.width = W; cv.height = H; }
      ctx.clearRect(0, 0, W, H);
      const s = Site.reduceMotion ? 0.8 : Math.sin((performance.now() - t0) / 1000 * 2 * Math.PI * 0.35);
      AX.forEach((a, k) => {
        const pw = narrow ? W : W / 3, ph = narrow ? H / 3 : H, px = narrow ? 0 : k * pw, py = narrow ? k * ph : 0;
        const pose = [0, 0, 0, 0, 0, 0]; pose[a.i] = a.amp * s;
        let P = null;
        ctx.save(); ctx.translate(px, py); ctx.beginPath(); ctx.rect(0, 0, pw, ph); ctx.clip();
        HX.draw(ctx, pw, ph, { legs: [0, 1, 2, 3, 4, 5], pose, angles: HX.bodyIK(pose), az: -0.75, el: 0.45, scale: narrow ? 0.62 : 0.58, body: true, cy: 0.66, gridR: 280, under: (c, p) => { P = p; } }, C);
        // the axis this rotation turns about, through the body centre
        const ends = a.i === 3 ? [[-200, 0, 0], [210, 0, 0]] : a.i === 4 ? [[0, -200, 0], [0, 210, 0]] : [[0, 0, 0], [0, 0, 120]];
        seg(ctx, P(ends[0]), P([0, 0, 0]), C.accent, 2, [4, 5]); arrow(ctx, P([0, 0, 0]), P(ends[1]), C.accent, 3);
        label(ctx, `${a.k} ${(a.amp * s).toFixed(0).padStart(3)}°`, [16, 28], C.ink, 16);
        label(ctx, t('rpy_' + a.k), [16, 50], C.muted, 13);
        ctx.restore();
        if (k) { ctx.strokeStyle = C.line; ctx.lineWidth = 1; ctx.beginPath(); if (narrow) { ctx.moveTo(0, py); ctx.lineTo(W, py); } else { ctx.moveTo(px, 0); ctx.lineTo(px, H); } ctx.stroke(); }
      });
      if (on && !Site.reduceMotion) requestAnimationFrame(draw);
    }
    watch(cv, v => { const w = on; on = v; if (on && !w) requestAnimationFrame(draw); });
    addEventListener('resize', () => { if (!on) draw(); });
    Site.onLang(draw); Site.onTheme(draw); draw();
  }

  /* ---------- 3. the chain, one step at a time ---------- */
  {
    const cv = $('chain'), ctx = cv.getContext('2d');
    const T = [20, 0], YAW = 10 * D, AL = R1.a * D;
    const M = (() => { const r = R2(YAW, R1.m); return [T[0] + r[0], T[1] + r[1]]; })();     // R1's coxa mount, in world
    const d = [FOOT[0] - T[0], FOOT[1] - T[1]], pB = R2(-YAW, d), q = [pB[0] - R1.m[0], pB[1] - R1.m[1]], pL = R2(-AL, q);
    const th = HX.ik(pL[0], pL[1], FOOT[2]);
    // per step: where the camera looks, how far it is turned, which frame is active, the vector shown
    const STEPS = [
      { c: [110, -40], rot: 0, frame: 'w', from: [0, 0], v: FOOT.slice(0, 2), name: 'f' },
      { c: [110, -40], rot: 0, frame: 'w', from: T, v: d, name: 'f − t' },
      { c: [120, -50], rot: YAW, frame: 'b', from: T, v: pB, name: 'pᴮ = Rᵀ(f − t)' },
      { c: [120, -50], rot: YAW, frame: 'b', from: M, v: q, name: 'pᴮ − m' },
      { c: [M[0] + 30, M[1] - 40], rot: YAW + AL, frame: 'l', from: M, v: pL, name: 'pᴸ = Rz(−α)(pᴮ − m)' }];
    let step = 0, cam = { c: STEPS[0].c.slice(), rot: 0 }, anim = null, playing = false, on = false, timer = 0, started = false;
    const ease = u => u < 0.5 ? 2 * u * u : 1 - (-2 * u + 2) ** 2 / 2;
    const fcol = f => f === 'w' ? C.blue : f === 'b' ? C.accent : C.good;
    function go(k) {
      step = (k + STEPS.length) % STEPS.length;
      anim = { a: { c: cam.c.slice(), rot: cam.rot }, b: STEPS[step], t0: performance.now(), dur: Site.reduceMotion ? 1 : 900 };
      $('chTxt').innerHTML = `<b>${step} / 4</b> · ` + t('ch' + step);
      requestAnimationFrame(draw);
    }
    function draw(now) {
      now = now || performance.now();
      const narrow = cv.clientWidth > 0 && cv.clientWidth < 620, W = narrow ? 440 : 1100, H = narrow ? 770 : 540;
      if (cv.width !== W || cv.height !== H) { cv.width = W; cv.height = H; }
      if (anim) {
        const u = Math.min(1, (now - anim.t0) / anim.dur), e = ease(u);
        cam = { c: [0, 1].map(i => anim.a.c[i] + (anim.b.c[i] - anim.a.c[i]) * e), rot: anim.a.rot + (anim.b.rot - anim.a.rot) * e };
        if (u >= 1) anim = null;
      }
      ctx.clearRect(0, 0, W, H);
      const s = narrow ? 0.95 : 1.35, ox = narrow ? 290 : 400, oy = narrow ? 250 : 280;
      const P = p => { const r = R2(-cam.rot, [p[0] - cam.c[0], p[1] - cam.c[1]]); return [ox - s * r[1], oy - s * r[0]]; };
      const S = STEPS[step];
      poly(ctx, HEX.map(m => P(m)), null, C.line, 1.5, [5, 5]);                       // body at home
      poly(ctx, HEX.map(m => { const r = R2(YAW, m); return P([T[0] + r[0], T[1] + r[1]]); }), C.body, C.ink, 1.5);
      seg(ctx, P(M), P(FOOT), C.line, 9); dot(ctx, P(M), 6, C.ink);                   // R1, seen from above
      const fr = (f, o, a, len, col, nm) => axes(ctx, P, o, a, len, S.frame === f ? col : C.line, S.frame === f ? 3 : 1.5, S.frame === f ? nm : null);
      fr('w', [0, 0], 0, 140, C.blue, ['x_world', 'y_world']);
      fr('b', T, YAW, 140, C.accent, ['x_body', 'y_body']);
      fr('l', M, YAW + AL, 120, C.good, ['x_leg', 'y_leg']);
      if (step >= 1) { const a = P([0, 0]), b = P(T); arrow(ctx, a, b, C.muted, 1.5); label(ctx, 't', [(a[0] + b[0]) / 2 + 8, (a[1] + b[1]) / 2 + 4], C.muted, 13); }
      if (step >= 3) { const a = P(T), b = P(M); arrow(ctx, a, b, C.muted, 1.5); label(ctx, 'm', [(a[0] + b[0]) / 2 - 6, (a[1] + b[1]) / 2 - 8], C.muted, 13, 'right'); }
      const F = P(FOOT), A = P(S.from), col = fcol(S.frame);
      arrow(ctx, A, F, col, 4);
      if (step === 4 && th) {           // theta1: the angle between x_leg and the foot
        const a0 = YAW + AL, a1 = a0 + th[0] * D, r = 60;
        ctx.strokeStyle = C.good; ctx.lineWidth = 2; ctx.beginPath();
        for (let k = 0; k <= 20; k++) { const a = a0 + (a1 - a0) * k / 20, p = P([M[0] + r * Math.cos(a), M[1] + r * Math.sin(a)]); k ? ctx.lineTo(p[0], p[1]) : ctx.moveTo(p[0], p[1]); }
        ctx.stroke(); const pm = P([M[0] + (r + 18) * Math.cos((a0 + a1) / 2), M[1] + (r + 18) * Math.sin((a0 + a1) / 2)]); label(ctx, 'θ1', [pm[0], pm[1] + 5], C.good, 14, 'center');
      }
      dot(ctx, F, 8, C.accent); label(ctx, t('chFoot'), [F[0] + 12, F[1] + 4], C.ink, 13);
      // ledger: every step's vector, the current one highlighted
      const lx = narrow ? 18 : 690, ly = narrow ? 482 : 56;
      label(ctx, t('chLedger'), [lx, ly], C.muted, 13);
      STEPS.forEach((st, k) => {
        const y = ly + 30 + k * (narrow ? 46 : 50), later = k > step;
        if (k === step) { ctx.fillStyle = C.accentSoft; ctx.fillRect(lx - 10, y - 21, narrow ? 420 : 396, 46); }
        ctx.globalAlpha = later ? 0.45 : 1;
        label(ctx, `${k}  ${st.name}`, [lx, y], later ? C.muted : C.ink, 14);
        label(ctx, `= ${vec(st.v)}  ${t('chIn_' + st.frame)}`, [lx + 24, y + 19], later ? C.muted : fcol(st.frame), 13);
        ctx.globalAlpha = 1;
      });
      if (step === 4 && th) label(ctx, `ik(pᴸ) → θ = (${th.map(v => v.toFixed(1) + '°').join(', ')})`, [lx, ly + 30 + 5 * (narrow ? 46 : 50)], C.good, 14);
      if (anim) requestAnimationFrame(draw);
    }
    const stopPlay = () => { playing = false; clearInterval(timer); $('chPlay').setAttribute('aria-pressed', 'false'); };
    const startPlay = () => { playing = true; $('chPlay').setAttribute('aria-pressed', 'true'); clearInterval(timer); timer = setInterval(() => { if (on) go(step + 1); }, 2800); };
    $('chPrev').addEventListener('click', () => { stopPlay(); go(step - 1); });
    $('chNext').addEventListener('click', () => { stopPlay(); go(step + 1); });
    $('chPlay').addEventListener('click', () => playing ? stopPlay() : startPlay());
    watch(cv, v => { on = v; if (v && !started && !Site.reduceMotion) { started = true; startPlay(); } });
    addEventListener('resize', () => requestAnimationFrame(draw));
    Site.onLang(() => go(step)); Site.onTheme(() => requestAnimationFrame(draw));
    go(0);
  }

  /* ---------- 4. the full pose widget ---------- */
  {
    const ids = ['px', 'py', 'pz', 'pr', 'pp', 'pw'], units = ['mm', 'mm', 'mm', '°', '°', '°'];
    const ins = ids.map($);
    const cv = $('pose'), ctx = cv.getContext('2d');
    let az = -0.7, drag = null, waving = false, on = false, t0 = 0;
    cv.addEventListener('pointerdown', e => { drag = e.clientX; cv.setPointerCapture(e.pointerId); });
    cv.addEventListener('pointermove', e => { if (drag != null) { az += (e.clientX - drag) * 0.01; drag = e.clientX; if (!waving) draw(); } });
    cv.addEventListener('pointerup', () => drag = null);
    // our wave dance: body rides a travelling wave, z = A sin(wt), pitch follows the wave's slope
    const A = 15, K = 2 * Math.PI / 600, W = 2 * Math.PI * 0.5;
    const wavePose = s => [0, 0, A * Math.sin(W * s), 0, -Math.atan(A * K * Math.cos(W * s)) * 180 / Math.PI, 0];
    function draw() {
      const pose = waving ? wavePose((performance.now() - t0) / 1000) : ins.map(i => +i.value);
      if (waving) ins.forEach((inp, k) => { inp.value = pose[k].toFixed(1); inp.parentElement.querySelector('output').textContent = `${pose[k].toFixed(1)} ${units[k]}`; });
      const ang = HX.bodyIK(pose);
      HX.draw(ctx, cv.width, cv.height, { legs: [0, 1, 2, 3, 4, 5], pose, angles: ang, az, el: 0.5, scale: 1.05, body: true, cy: 0.62, gridR: 400 }, C);
      Site.kv($('pkv'), HX.LEGS.map((l, i) => [l.n, ang[i] ? ang[i].map(v => (Math.abs(v) < 0.5 ? 0 : v).toFixed(0).padStart(4)).join(' ') + '°' : `<span style="color:var(--bad)">✗ ${t('w_fail')}</span>`]));
      if (waving && on && !Site.reduceMotion) requestAnimationFrame(draw);
    }
    ins.forEach((inp, k) => Site.slider(inp, v => `${(+v).toFixed(1)} ${units[k]}`, () => { if (!waving) draw(); }));
    const stopWave = () => { waving = false; $('wave').setAttribute('aria-pressed', 'false'); };
    $('reset').addEventListener('click', () => { stopWave(); ins.forEach(i => { i.value = 0; i.dispatchEvent(new Event('input')); }); });
    $('wave').addEventListener('click', () => {
      if (waving) { stopWave(); draw(); return; }
      waving = true; t0 = performance.now(); $('wave').setAttribute('aria-pressed', 'true'); requestAnimationFrame(draw);
    });
    ins.forEach(i => i.addEventListener('pointerdown', stopWave));
    watch(cv, v => { const w = on; on = v; if (on && !w && waving) requestAnimationFrame(draw); });
    Site.onLang(draw); Site.onTheme(draw);
    draw();
  }
})();
