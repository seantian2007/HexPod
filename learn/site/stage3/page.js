(() => {
  const $ = id => document.getElementById(id);
  const D2R = Math.PI / 180, L1 = 62, L2 = 76, L3 = 132;
  const C = Site.C, t = Site.t, { dragOn, grid, seg, dot, label, cross } = Site.cv, kv = Site.kv, pill = Site.pill;

  const f1 = v => v.toFixed(1);

  /* ---------- top view (θ1) ---------- */
  const tv = $('top'), tc = tv.getContext('2d'), TS = 1.55, TO = [150, 270];
  let tgt = [162, 60];
  function drawTop() {
    const W = tv.width, H = tv.height; tc.clearRect(0, 0, W, H); grid(tc, W, H, TO[0], TO[1], TS, 20);
    // body edge
    tc.fillStyle = C.body; tc.fillRect(0, TO[1] - 70, TO[0] - 20, 140); label(tc, 'body', [14, TO[1] + 5], C.muted, 15);
    // legal wedge
    tc.fillStyle = C.blueSoft; tc.beginPath(); tc.moveTo(TO[0], TO[1]); tc.arc(TO[0], TO[1], 330, -45 * D2R, 45 * D2R); tc.closePath(); tc.fill();
    seg(tc, TO, [TO[0] + 360, TO[1]], C.muted, 1, [3, 4]); label(tc, 'x', [TO[0] + 362, TO[1] - 6], C.muted, 13);
    const th = Math.atan2(tgt[1], tgt[0]), r = Math.hypot(tgt[0], tgt[1]), legal = Math.abs(th / D2R) <= 45;
    const P = (x, y) => [TO[0] + x * TS, TO[1] - y * TS];
    const fem = P(L1 * Math.cos(th), L1 * Math.sin(th)), T = P(tgt[0], tgt[1]);
    seg(tc, P(0, 0), fem, legal ? C.ink : C.bad, 8);
    seg(tc, fem, T, legal ? C.accent : C.bad, 3, [8, 6]);
    dot(tc, P(0, 0), 6, C.ink); dot(tc, fem, 5, C.ink);
    tc.strokeStyle = C.blue; tc.lineWidth = 2; tc.beginPath(); tc.arc(TO[0], TO[1], 46, 0, -th, th > 0); tc.stroke();
    label(tc, 'θ1', [TO[0] + 60 * Math.cos(th / 2) + 4, TO[1] - 60 * Math.sin(th / 2) + 6], C.blue, 19);
    label(tc, 'L1 = 62', [TO[0] - 10, TO[1] + (th > 0 ? 34 : -22)], C.muted, 15);
    label(tc, 'u', [(fem[0] + T[0]) / 2 + 6, (fem[1] + T[1]) / 2 - 10], C.accent, 19);
    cross(tc, T, legal ? C.ink : C.bad);
    label(tc, `${t('w_target')} (${tgt[0].toFixed(0)}, ${tgt[1].toFixed(0)})`, [T[0] + 18, T[1] - 16], C.muted, 16);
    kv($('topKV'), [['x, y', `${f1(tgt[0])}, ${f1(tgt[1])} mm`], ['θ1 = atan2(y,x)', `${f1(th / D2R)}°`], ['r = √(x²+y²)', `${f1(r)} mm`], ['u = r − 62', `${f1(r - L1)} mm`]]);
    $('topSt').innerHTML = pill(legal, legal ? `θ1 ${t('w_legal')} (±45°)` : `θ1 ${t('w_out')} (±45°)`);
  }
  dragOn(tv, p => { tgt = [(p[0] - TO[0]) / TS, (TO[1] - p[1]) / TS]; drawTop(); });

  /* ---------- side view (θ2, θ3) ---------- */
  const sv = $('side'), sc = sv.getContext('2d'), SS = 1.4, SO = [210, 250];
  let foot = [100, -89.5], down = false;
  function drawSide() {
    const W = sv.width, H = sv.height; sc.clearRect(0, 0, W, H); grid(sc, W, H, SO[0], SO[1], SS, 20);
    const P = (u, z) => [SO[0] + u * SS, SO[1] - z * SS];
    // reach ring
    sc.fillStyle = C.blueSoft; sc.beginPath(); sc.arc(SO[0], SO[1], (L2 + L3) * SS, 0, 7); sc.arc(SO[0], SO[1], (L3 - L2) * SS, 0, 7, true); sc.fill();
    label(sc, '208 mm', [SO[0] + 208 * SS * 0.71 + 8, SO[1] + 208 * SS * 0.71], C.blue, 15); label(sc, '56', [SO[0] - 30, SO[1] + 72], C.blue, 15);
    // coxa stub + horizontal
    seg(sc, P(-L1, 0), P(0, 0), C.muted, 7); dot(sc, P(-L1, 0), 5, C.muted); label(sc, 'coxa', [SO[0] - L1 * SS - 10, SO[1] - 16], C.muted, 15);
    seg(sc, P(0, 0), P(215, 0), C.muted, 1, [3, 4]);
    const [u, z] = foot, D = Math.hypot(u, z), c = (D * D - L2 * L2 - L3 * L3) / (2 * L2 * L3), reach = Math.abs(c) <= 1;
    const cc = Math.max(-1, Math.min(1, c));
    let t3 = Math.acos(cc); if (down) t3 = -t3;
    const al = Math.atan2(z, u), be = Math.atan2(L3 * Math.sin(t3), L2 + L3 * Math.cos(t3)), t2 = al + be;
    const knee = [L2 * Math.cos(t2), L2 * Math.sin(t2)], toe = [knee[0] + L3 * Math.cos(t2 - t3), knee[1] + L3 * Math.sin(t2 - t3)];
    const t2d = t2 / D2R, t3d = t3 / D2R, ok2 = Math.abs(t2d) <= 75, ok3 = t3d >= 15 && t3d <= 165;
    // D line + arcs
    seg(sc, P(0, 0), P(u, z), C.muted, 2, [6, 5]); label(sc, 'D', P(u / 2 + 8, z / 2 - 8), C.muted, 19);
    sc.lineWidth = 2; sc.strokeStyle = C.good; sc.beginPath(); sc.arc(SO[0], SO[1], 52, 0, -al, al > 0); sc.stroke();
    label(sc, 'α', [SO[0] + 58 * Math.cos(al / 2), SO[1] - 58 * Math.sin(al / 2) + 6], C.good, 19);
    sc.strokeStyle = C.accent; sc.beginPath(); sc.arc(SO[0], SO[1], 76, -al, -(al + be), be > 0); sc.stroke();
    label(sc, 'β', [SO[0] + 84 * Math.cos(al + be / 2), SO[1] - 84 * Math.sin(al + be / 2) + 6], C.accent, 19);
    // links
    seg(sc, P(0, 0), P(...knee), reach && ok2 ? C.blue : C.bad, 9);
    seg(sc, P(...knee), P(...toe), reach && ok3 ? C.ink : C.bad, 7);
    dot(sc, P(0, 0), 7, C.ink); dot(sc, P(...knee), 6, C.ink); dot(sc, P(...toe), 6, reach ? C.accent : C.bad);
    label(sc, 'femur', P(knee[0] / 2 - 46, knee[1] / 2 + 14), C.blue, 15);
    label(sc, 'θ3', P(knee[0] + 10, knee[1] + 12), C.ink, 19);
    cross(sc, P(u, z), reach ? C.ink : C.bad);
    kv($('sideKV'), [['u, z', `${f1(u)}, ${f1(z)} mm`], ['D', `${f1(D)} mm`], ['cos θ3', reach ? c.toFixed(3) : `${c.toFixed(3)} ✗`], ['θ3', reach ? `${f1(t3d)}°` : '—'], ['α', `${f1(al / D2R)}°`], ['β', reach ? `${f1(be / D2R)}°` : '—'], ['θ2 = α ' + (down ? '−' : '+') + ' β', reach ? `${f1(t2d)}°` : '—']]);
    let st = '';
    if (!reach) st = pill(false, `${t('w_noreach')}: D ${D > 208 ? '> 208' : '< 56'}`);
    else if (ok2 && ok3) st = pill(true, t('w_ok'));
    else st = (ok2 ? '' : pill(false, `θ2 ${t('w_limit')} ±75°`) + ' ') + (ok3 ? '' : pill(false, `θ3 ${t('w_limit')} 15…165°`));
    $('sideSt').innerHTML = st;
  }
  dragOn(sv, p => { foot = [(p[0] - SO[0]) / SS, (SO[1] - p[1]) / SS]; drawSide(); });
  $('flip').addEventListener('click', () => { down = !down; $('flip').setAttribute('aria-pressed', String(down)); drawSide(); });

  /* ---------- hero: dancing hexapod ---------- */
  const hv = $('hero'), hc = hv.getContext('2d');
  let az = -0.75, spin = true, t0 = performance.now(), lastX = null, heroOn = true;
  hv.addEventListener('pointerdown', e => { lastX = e.clientX; spin = false; hv.setPointerCapture(e.pointerId); });
  hv.addEventListener('pointermove', e => { if (lastX != null) { az += (e.clientX - lastX) * 0.01; lastX = e.clientX; } });
  hv.addEventListener('pointerup', () => { lastX = null; });
  const reduce = Site.reduceMotion;
  new IntersectionObserver(es => es.forEach(e => { const was = heroOn; heroOn = e.isIntersecting; if (heroOn && !was) requestAnimationFrame(frame); })).observe(hv);
  function frame(now) {
    const tt = reduce ? 0 : (now - t0) / 1000;
    if (spin && !reduce) az = -0.75 + 0.12 * tt;
    const pose = HX.danceT(tt), ang = HX.bodyIK(pose);
    HX.draw(hc, hv.width, hv.height, { legs: [0, 1, 2, 3, 4, 5], pose, angles: ang, az, el: 0.5, scale: 1.25, body: true, cy: 0.6 }, C);
    if (heroOn && !reduce) requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);

  /* ---------- flatten: 3D leg plane (left) and the 2D sheet (right) ---------- */
  const pv = $('plane'), pc = pv.getContext('2d');
  let pOn = false;
  const pT0 = performance.now();
  function drawPlane(now) {
    const W = pv.width, H = pv.height, tt = Site.reduceMotion ? 1.3 : (now - pT0) / 1000;
    pc.clearRect(0, 0, W, H);
    const phi = 32 * Math.sin(tt * 0.7) * D2R, rr = 175 + 25 * Math.sin(tt * 1.1), zz = -80 + 30 * Math.sin(tt * 0.9 + 1);
    const tgt3 = [rr * Math.cos(phi), rr * Math.sin(phi), zz], ang = HX.ik(...tgt3);
    // left: oblique 3D view
    const az = -1.05, el = 0.42, s = 1.25, cx = 170, cy = 250;
    const P = p => { const xr = p[0] * Math.cos(az) - p[1] * Math.sin(az), yr = p[0] * Math.sin(az) + p[1] * Math.cos(az); return [cx + s * xr, cy - s * (p[2] * Math.cos(el) + yr * Math.sin(el))]; };
    const gz = -120;
    pc.strokeStyle = C.grid; pc.lineWidth = 1;
    for (let k = -120; k <= 280; k += 40) {
      let a = P([k, -160, gz]), b = P([k, 160, gz]); pc.beginPath(); pc.moveTo(...a); pc.lineTo(...b); pc.stroke();
      a = P([-120, k - 120, gz]); b = P([280, k - 120, gz]); pc.beginPath(); pc.moveTo(...a); pc.lineTo(...b); pc.stroke();
    }
    const dir = [Math.cos(phi), Math.sin(phi)], q = (d, z) => P([d * dir[0], d * dir[1], z]);
    // the vertical sheet
    const quad = [q(0, 70), q(260, 70), q(260, gz), q(0, gz)];
    pc.fillStyle = C.blueSoft; pc.globalAlpha = 0.75; pc.beginPath(); quad.forEach((p, i) => i ? pc.lineTo(...p) : pc.moveTo(...p)); pc.closePath(); pc.fill(); pc.globalAlpha = 1;
    pc.strokeStyle = C.blue; pc.lineWidth = 1.2; pc.stroke();
    label(pc, t('pl_sheet'), [quad[1][0] - 8, quad[1][1] + 20], C.blue, 14, 'right');
    // x axis and θ1 arc at coxa height
    seg(pc, P([0, 0, 0]), P([240, 0, 0]), C.muted, 1, [4, 4]); label(pc, 'x', P([250, 0, 0]), C.muted, 13);
    pc.strokeStyle = C.accent; pc.lineWidth = 2.5; pc.beginPath();
    for (let k = 0; k <= 20; k++) { const a = phi * k / 20, p = P([60 * Math.cos(a), 60 * Math.sin(a), 0]); k ? pc.lineTo(...p) : pc.moveTo(...p); }
    pc.stroke();
    label(pc, 'θ1', P([82 * Math.cos(phi / 2), 82 * Math.sin(phi / 2), 0]), C.accent, 16);
    // target, its drop line and the leg
    const T = P(tgt3), Tg = P([tgt3[0], tgt3[1], 0]);
    seg(pc, Tg, T, C.muted, 1.2, [3, 4]); seg(pc, P([0, 0, 0]), Tg, C.muted, 1.2, [3, 4]);
    const rl = P([rr * 0.6 * dir[0], rr * 0.6 * dir[1], 0]);
    label(pc, 'r', [rl[0], rl[1] - 8], C.muted, 15);
    if (ang) {
      const pts = HX.legPts(ang).map(P);
      [[0, 1, 6, C.muted], [1, 2, 8, C.blue], [2, 3, 6, C.ink]].forEach(([a, b, w, c]) => seg(pc, pts[a], pts[b], c, w));
      pts.slice(0, 3).forEach(p => dot(pc, p, 4.5, C.ink));
    }
    cross(pc, T, C.ink);
    seg(pc, P([0, 0, -30]), P([0, 0, 50]), C.ink, 2, [2, 3]);
    label(pc, 'coxa', [P([0, 0, 50])[0] - 18, P([0, 0, 50])[1] - 8], C.muted, 13);
    // right: the sheet, drawn flat
    const ox = 660, oy = 190, s2 = 1.3;
    pc.fillStyle = C.blueSoft; pc.fillRect(ox - 100, 24, 450, 410); pc.strokeStyle = C.blue; pc.lineWidth = 1.2; pc.strokeRect(ox - 100, 24, 450, 410);
    const Q = (u, z) => [ox + u * s2, oy - z * s2];
    seg(pc, Q(-62, 0), Q(250, 0), C.muted, 1, [4, 4]);
    const u = rr - L1;
    if (ang) {
      const r2 = HX.legPts(ang).map(p => [Math.hypot(p[0], p[1]) - L1, p[2]]);
      seg(pc, Q(-62, 0), Q(0, 0), C.muted, 6); seg(pc, Q(0, 0), Q(...r2[2]), C.blue, 8); seg(pc, Q(...r2[2]), Q(...r2[3]), C.ink, 6);
      dot(pc, Q(0, 0), 5, C.ink); dot(pc, Q(...r2[2]), 5, C.ink); dot(pc, Q(-62, 0), 5, C.muted);
    }
    cross(pc, Q(u, zz), C.ink);
    seg(pc, Q(0, zz - 24), Q(u, zz - 24), C.accent, 2.5); label(pc, `u = ${u.toFixed(0)}`, Q(u / 2, zz - 44), C.accent, 15, 'center');
    seg(pc, Q(u + 20, 0), Q(u + 20, zz), C.good, 2.5); label(pc, `z = ${zz.toFixed(0)}`, Q(u + 28, zz / 2), C.good, 15);
    label(pc, t('pl_femur'), Q(-70, -22), C.muted, 13);
    label(pc, t('pl_title'), [ox - 88, 48], C.blue, 14);
    if (pOn && !Site.reduceMotion) requestAnimationFrame(drawPlane);
  }
  new IntersectionObserver(es => es.forEach(e => { const was = pOn; pOn = e.isIntersecting; if (pOn && !was) requestAnimationFrame(drawPlane); })).observe(pv);

  const redraw = () => { drawTop(); drawSide(); if (!pOn || Site.reduceMotion) drawPlane(performance.now()); };
  Site.onLang(redraw); Site.onTheme(redraw);
  redraw();
})();
