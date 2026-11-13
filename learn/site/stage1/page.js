(() => {
  const $ = id => document.getElementById(id);
  const C = Site.C, t = Site.t, { grid, seg, dot, label, arrow } = Site.cv, D2R = Site.D2R;
  const L1 = 62, L2 = 76, L3 = 132;
  const ONE = [{ n: 'leg', m: [0, 0], a: 0 }];
  const fk = (a1, a2, a3) => { const r = L1 + L2 * Math.cos(a2 * D2R) + L3 * Math.cos((a2 - a3) * D2R), z = L2 * Math.sin(a2 * D2R) + L3 * Math.sin((a2 - a3) * D2R); return [r * Math.cos(a1 * D2R), r * Math.sin(a1 * D2R), z, r]; };
  const f1 = v => v.toFixed(1);

  /* ---------- hero: one leg sweeping, the foot leaves a trail ---------- */
  const hv = $('hero'), hc = hv.getContext('2d');
  let heroOn = true, trailH = [];
  const t0 = performance.now();
  function hero(now) {
    const tt = Site.reduceMotion ? 2 : (now - t0) / 1000;
    const a = [35 * Math.sin(0.45 * tt), 40 * Math.sin(0.8 * tt + 1), 95 + 55 * Math.sin(1.13 * tt)];
    const p = fk(...a); trailH.push([p[0], p[1], p[2]]); if (trailH.length > 520) trailH.shift();
    HX.draw(hc, hv.width, hv.height, { legDefs: ONE, legs: [0], angles: [a], pose: [0, 0, 0, 0, 0, 0], az: -0.55 + 0.08 * Math.sin(tt * 0.2), el: 0.42, scale: 1.9, ox: -200, cy: 0.62, ground: 130, gridR: 280, trails: [trailH] }, C);
    if (heroOn && !Site.reduceMotion) requestAnimationFrame(hero);
  }
  new IntersectionObserver(es => es.forEach(e => { const w = heroOn; heroOn = e.isIntersecting; if (heroOn && !w) requestAnimationFrame(hero); })).observe(hv);
  requestAnimationFrame(hero);

  /* ---------- side view: θ2, θ3 → (r, z) ---------- */
  const sv = $('side'), sc = sv.getContext('2d'), S = 1.35, O = [150, 250];
  const s2 = $('t2'), s3 = $('t3');
  function drawSide() {
    const a2 = +s2.value, a3 = +s3.value, W = sv.width, H = sv.height;
    sc.clearRect(0, 0, W, H); grid(sc, W, H, O[0], O[1], S, 20);
    const P = (r, z) => [O[0] + r * S, O[1] - z * S];
    seg(sc, P(0, -170), P(0, 150), C.muted, 1.5, [2, 4]); label(sc, t('w_axis'), [O[0] + 6, 26], C.muted, 13);
    seg(sc, P(0, 0), P(330, 0), C.muted, 1, [4, 4]);
    const hip = [L1, 0], knee = [L1 + L2 * Math.cos(a2 * D2R), L2 * Math.sin(a2 * D2R)], [, , z, r] = fk(0, a2, a3);
    seg(sc, P(0, 0), P(...hip), C.muted, 7);
    seg(sc, P(...hip), P(...knee), C.blue, 9); seg(sc, P(...knee), P(r, z), C.ink, 7);
    // femur extension and angle arcs
    const ext = [knee[0] + 60 * Math.cos(a2 * D2R), knee[1] + 60 * Math.sin(a2 * D2R)];
    seg(sc, P(...knee), P(...ext), C.muted, 1.2, [5, 4]);
    const arc = (c, r0, from, to, col) => { sc.strokeStyle = col; sc.lineWidth = 2.5; sc.beginPath(); sc.arc(...P(...c), r0, -from * D2R, -to * D2R, to > from); sc.stroke(); };
    arc(hip, 50, 0, a2, C.accent); label(sc, 'θ2', P(hip[0] + 48 * Math.cos(a2 / 2 * D2R) / S + 6, hip[1] + 48 * Math.sin(a2 / 2 * D2R) / S), C.accent, 17);
    arc(knee, 40, a2, a2 - a3, C.accent); const mid = (a2 - a3 / 2) * D2R; label(sc, 'θ3', P(knee[0] + 58 * Math.cos(mid) / S, knee[1] + 58 * Math.sin(mid) / S), C.accent, 17);
    // r and z projections
    seg(sc, P(0, z - 18 / S), P(r, z - 18 / S), C.good, 2.5); label(sc, `r = ${f1(r)}`, P(r / 2, z - 34 / S), C.good, 15, 'center');
    seg(sc, P(r + 14 / S, 0), P(r + 14 / S, z), C.blue, 2.5); label(sc, `z = ${f1(z)}`, P(r + 22 / S, z / 2), C.blue, 15);
    dot(sc, P(0, 0), 5, C.muted); dot(sc, P(...hip), 6, C.ink); dot(sc, P(...knee), 6, C.ink); dot(sc, P(r, z), 7, C.accent);
    label(sc, 'L1', P(L1 / 2 - 6, 10), C.muted, 13); label(sc, 'L2', P((hip[0] + knee[0]) / 2 - 22, (hip[1] + knee[1]) / 2 + 8), C.blue, 13); label(sc, 'L3', P((knee[0] + r) / 2 + 10, (knee[1] + z) / 2), C.ink, 13);
    Site.kv($('skv'), [['r', `${f1(r)} mm`], ['z', `${f1(z)} mm`], [t('w_tibAbs'), `${a2 - a3}°`]]);
  }
  Site.slider(s2, v => `${v}°`, drawSide); Site.slider(s3, v => `${v}°`, drawSide);

  /* ---------- 3D: all three angles ---------- */
  const lv = $('leg3'), lc = lv.getContext('2d'), b1 = $('a1'), b2 = $('a2'), b3 = $('a3');
  let az = -0.8, drag = null, trail = [], trailOn = false;
  lv.addEventListener('pointerdown', e => { drag = e.clientX; lv.setPointerCapture(e.pointerId); });
  lv.addEventListener('pointermove', e => { if (drag != null) { az += (e.clientX - drag) * 0.01; drag = e.clientX; draw3(); } });
  lv.addEventListener('pointerup', () => drag = null);
  function draw3() {
    const a = [+b1.value, +b2.value, +b3.value], p = fk(...a);
    if (trailOn) { trail.push([p[0], p[1], p[2]]); if (trail.length > 4000) trail.shift(); }
    HX.draw(lc, lv.width, lv.height, { legDefs: ONE, legs: [0], angles: [a], pose: [0, 0, 0, 0, 0, 0], az, el: 0.45, scale: 1.55, ox: -130, cy: 0.64, ground: 130, gridR: 280, trails: trailOn ? [trail] : [] }, C);
    Site.kv($('lkv'), [['x', `${f1(p[0])} mm`], ['y', `${f1(p[1])} mm`], ['z', `${f1(p[2])} mm`], ['r', `${f1(p[3])} mm`]]);
  }
  [b1, b2, b3].forEach(b => Site.slider(b, v => `${v}°`, draw3));
  $('trail').addEventListener('click', e => { trailOn = !trailOn; e.currentTarget.setAttribute('aria-pressed', String(trailOn)); if (!trailOn) trail = []; draw3(); });

  /* ---------- refresher: cos and sin as the shadows of one link ---------- */
  const tv = $('trig'), tc = tv.getContext('2d'), tp = $('phi'), LT = 132;
  const setPhi = v => { tp.value = v; tp.dispatchEvent(new Event('input')); };
  function drawTrig() {
    const W = tv.width, H = tv.height, ph = +tp.value, a = ph * D2R, S = 1.5, O = [W / 2, H / 2];
    tc.clearRect(0, 0, W, H); grid(tc, W, H, O[0], O[1], S, 20);
    const P = (x, z) => [O[0] + x * S, O[1] - z * S];
    seg(tc, P(-170, 0), P(170, 0), C.muted, 1.2); seg(tc, P(0, -150), P(0, 150), C.muted, 1.2);
    label(tc, t('tg_h'), P(172, 4), C.muted, 13, 'right'); label(tc, t('tg_v'), P(4, 146), C.muted, 13);
    tc.strokeStyle = C.line; tc.lineWidth = 1.5; tc.setLineDash([4, 5]); tc.beginPath(); tc.arc(O[0], O[1], LT * S, 0, 2 * Math.PI); tc.stroke(); tc.setLineDash([]);
    const c = Math.cos(a), s = Math.sin(a), E = [LT * c, LT * s], X = P(E[0], 0), Q = P(...E);
    if (Math.abs(s) > 0.06 && Math.abs(c) > 0.06) {
      const dx = -Math.sign(c) * 11, dy = Math.sign(s) * 11;
      tc.strokeStyle = C.muted; tc.lineWidth = 1.2; tc.beginPath(); tc.moveTo(X[0] + dx, X[1]); tc.lineTo(X[0] + dx, X[1] - dy); tc.lineTo(X[0], X[1] - dy); tc.stroke();
    }
    seg(tc, P(0, 0), X, C.good, 5); seg(tc, X, Q, C.blue, 5);
    seg(tc, P(0, 0), Q, C.ink, 8);
    tc.strokeStyle = C.accent; tc.lineWidth = 2.5; tc.beginPath(); tc.arc(O[0], O[1], 42, 0, -a, a > 0); tc.stroke();
    label(tc, 'φ', [O[0] + 58 * Math.cos(a / 2) - 5, O[1] - 58 * Math.sin(a / 2) + 6], C.accent, 18);
    dot(tc, P(0, 0), 5, C.ink); dot(tc, Q, 7, C.accent);
    label(tc, `L·cos φ = ${f1(E[0])}`, [(O[0] + X[0]) / 2, X[1] + (s >= 0 ? 24 : -14)], C.good, 15, 'center');
    label(tc, `L·sin φ = ${f1(E[1])}`, [X[0] + (c >= 0 ? 12 : -12), (X[1] + Q[1]) / 2 + 5], C.blue, 15, c >= 0 ? 'left' : 'right');
    label(tc, 'L = 132', [(O[0] + Q[0]) / 2 + (s * c >= 0 ? -12 : 12), (O[1] + Q[1]) / 2 + (s * c >= 0 ? -10 : -10)], C.ink, 14, s * c >= 0 ? 'right' : 'left');
    Site.kv($('tkv'), [['φ', `${ph}°`], ['cos φ', c.toFixed(3)], ['sin φ', s.toFixed(3)], ['L·cos φ', `${f1(E[0])} mm`], ['L·sin φ', `${f1(E[1])} mm`]]);
  }
  Site.cv.dragOn(tv, p => { const W = tv.width, H = tv.height; setPhi(Math.round(Math.atan2(H / 2 - p[1], p[0] - W / 2) / D2R)); });
  Site.slider(tp, v => `${v}°`, drawTrig);
  $('phiA').addEventListener('click', () => setPhi(30)); $('phiB').addEventListener('click', () => setPhi(-75));

  const redraw = () => { drawSide(); draw3(); drawTrig(); };
  Site.onLang(redraw); Site.onTheme(redraw);
  redraw();
})();
