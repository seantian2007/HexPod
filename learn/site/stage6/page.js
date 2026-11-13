(() => {
  const $ = id => document.getElementById(id);
  const C = Site.C, t = Site.t, { seg, dot, label } = Site.cv, D2R = Math.PI / 180;

  // gait tables, same as our gaits.py: [beta, offsets for R1 R2 R3 L1 L2 L3]
  const GAITS = { tripod: [1 / 2, [0, 1 / 2, 0, 1 / 2, 0, 1 / 2]], ripple: [2 / 3, [1 / 6, 5 / 6, 1 / 2, 2 / 3, 1 / 3, 0]], wave: [5 / 6, [1 / 3, 1 / 6, 0, 5 / 6, 2 / 3, 1 / 2]] };
  // period and speed caps per gait, same as our teleop: v_max = v * LIMIT, w_max = min(w * LIMIT, 21)
  const CFG = { tripod: { T: 2.5, v: 0.38, w: 0.15 }, ripple: { T: 3, v: 0.16, w: 0.075 }, wave: { T: 6, v: 0.075, w: 0.035 } };
  const LIMIT = 150, W_CAP = 21, H_LIFT = 30, DT = 0.02;
  const BETA_TXT = { tripod: '½', ripple: '⅔', wave: '⅚' };
  const vTop = g => CFG[g].v * LIMIT, wTop = g => Math.min(CFG[g].w * LIMIT, W_CAP);
  const HOME = HX.FEET.map(f => f.slice());
  const cyc = s => s - Math.sin(2 * Math.PI * s) / (2 * Math.PI);
  function legPhase(i, tt, T, g) { // -> [in stance, progress s]
    const [b, d] = GAITS[g], phi = (((tt / T - d[i]) % 1) + 1) % 1;
    return phi < b ? [true, phi / b] : [false, (phi - b) / (1 - b)];
  }
  function hull(pts) { // convex hull, counter-clockwise (monotone chain)
    const p = pts.slice().sort((a, b) => a[0] - b[0] || a[1] - b[1]), cr = (o, a, b) => (a[0] - o[0]) * (b[1] - o[1]) - (a[1] - o[1]) * (b[0] - o[0]);
    const lo = [], up = [];
    for (const q of p) { while (lo.length >= 2 && cr(lo[lo.length - 2], lo[lo.length - 1], q) <= 0) lo.pop(); lo.push(q); }
    for (const q of p.reverse()) { while (up.length >= 2 && cr(up[up.length - 2], up[up.length - 1], q) <= 0) up.pop(); up.push(q); }
    return lo.slice(0, -1).concat(up.slice(0, -1));
  }
  function margin(pts) { // distance from the origin (CoM) to the nearest support edge, and that edge's closest point
    if (pts.length < 3) return null;
    const h = hull(pts); let best = null;
    h.forEach((a, k) => {
      const b = h[(k + 1) % h.length], ex = b[0] - a[0], ey = b[1] - a[1], L = Math.hypot(ex, ey);
      const d = (ex * (0 - a[1]) - ey * (0 - a[0])) / L, u = Math.max(0, Math.min(1, (-a[0] * ex - a[1] * ey) / (L * L)));
      if (!best || d < best.d) best = { d, q: [a[0] + u * ex, a[1] + u * ey] };
    });
    return { d: best.d, q: best.q, hull: h };
  }

  /* ---------- 1. the gait timetable ---------- */
  const gc = $('gait'), gx = gc.getContext('2d'), gtIn = $('gt'), gtOut = gtIn.parentElement.querySelector('output');
  let gait = 'tripod', gt = 0.15, gplay = !Site.reduceMotion, gOn = false, gLast = 0;
  const ROWS = [3, 4, 5, 0, 1, 2]; // L1 L2 L3 above R1 R2 R3
  function feetAt(g, tt) {
    const b = GAITS[g][0], T = CFG[g].T, S = vTop(g) * b * T;
    return HOME.map((f, i) => {
      const [st, s] = legPhase(i, tt, T, g);
      return st ? { x: f[0] + S / 2 - S * s, y: f[1], st } : { x: f[0] - S / 2 + S * cyc(s), y: f[1], st, s };
    });
  }
  const worst = {};
  Object.keys(GAITS).forEach(g => { let m = Infinity; for (let k = 0; k < 600; k++) { const r = margin(feetAt(g, k / 600 * CFG[g].T).filter(f => f.st).map(f => [f.x, f.y])); if (r) m = Math.min(m, r.d); } worst[g] = m; });

  function drawGait() {
    // wide screens: timetable left, top view right. Narrow screens: stacked.
    const narrow = gc.clientWidth > 0 && gc.clientWidth < 620, Wt = narrow ? 560 : 1100, Ht = narrow ? 820 : 430;
    if (gc.width !== Wt) { gc.width = Wt; gc.height = Ht; }
    const W = gc.width, H = gc.height, ctx = gx; ctx.clearRect(0, 0, W, H);
    const lg = narrow ? [30, 58] : [400, 34], top = narrow ? 92 : 74;
    const [b, d] = GAITS[gait], x0 = 120, x1 = narrow ? 530 : 640, rh = 44, bh = 26, X = u => x0 + u / 2 * (x1 - x0);
    label(ctx, t('g_title'), [30, 34], C.ink, 15);
    ctx.fillStyle = C.accent; ctx.fillRect(lg[0], lg[1] - 11, 22, 12); label(ctx, t('g_ground'), [lg[0] + 28, lg[1]], C.muted, 12.5);
    ctx.strokeStyle = C.muted; ctx.lineWidth = 1; ctx.strokeRect(lg[0] + 130.5, lg[1] - 10.5, 22, 12); label(ctx, t('g_air'), [lg[0] + 158, lg[1]], C.muted, 12.5);
    ROWS.forEach((i, r) => {
      const y = top + r * rh + (r >= 3 ? 10 : 0), col = HX.COLORS[i];
      dot(ctx, [44, y + bh / 2], 6, col); label(ctx, HX.LEGS[i].n, [58, y + bh / 2 + 5], C.ink, 14);
      ctx.fillStyle = C.paper; ctx.strokeStyle = C.line; ctx.lineWidth = 1; ctx.fillRect(x0, y, x1 - x0, bh); ctx.strokeRect(x0 + .5, y + .5, x1 - x0 - 1, bh - 1);
      ctx.fillStyle = col; ctx.globalAlpha = 0.85;
      for (let u = -1; u <= 2; u++) { const a = Math.max(0, d[i] + u), e = Math.min(2, d[i] + u + b); if (e > a) ctx.fillRect(X(a), y + 1, X(e) - X(a), bh - 2); }
      ctx.globalAlpha = 1;
    });
    const yb = top + 6 * rh + 10;
    seg(ctx, [x0, top + 3 * rh + 2], [x1, top + 3 * rh + 2], C.line, 1, [3, 4]);
    [0, 0.5, 1, 1.5, 2].forEach(u => { seg(ctx, [X(u), yb - 2], [X(u), yb + 4], C.muted, 1); label(ctx, String(u), [X(u), yb + 20], C.muted, 12, 'center'); });
    label(ctx, 't / T', [x1, yb + 38], C.muted, 12, 'right');
    // time cursor
    const cxr = X(gt), feet = feetAt(gait, gt * CFG[gait].T), down = feet.filter(f => f.st).length;
    seg(ctx, [cxr, top - 12], [cxr, yb], C.ink, 2.5);
    label(ctx, `${down} ${t('g_down')}`, [cxr, top - 18], C.ink, 12.5, cxr > x1 - 60 ? 'right' : (cxr < x0 + 60 ? 'left' : 'center'));

    // top view
    const ox = narrow ? 280 : 880, oy = narrow ? 620 : 226, s = narrow ? 0.56 : 0.6, P = (x, y) => [ox - s * y, oy - s * x];
    label(ctx, t('g_top'), narrow ? [30, 440] : [700, 34], C.ink, 15);
    label(ctx, t('g_front'), [ox, oy - 168], C.muted, 12, 'center');
    const st = feet.filter(f => f.st).map(f => [f.x, f.y]), m = margin(st);
    if (m) {
      ctx.fillStyle = C.accentSoft; ctx.strokeStyle = C.accent; ctx.lineWidth = 2; ctx.beginPath();
      m.hull.forEach((p, k) => { const q = P(p[0], p[1]); k ? ctx.lineTo(q[0], q[1]) : ctx.moveTo(q[0], q[1]); }); ctx.closePath(); ctx.fill(); ctx.stroke();
    }
    feet.forEach((f, i) => { const l = HX.LEGS[i]; seg(ctx, P(l.m[0], l.m[1]), P(f.x, f.y), HX.COLORS[i], 5, f.st ? null : [2, 6]); });
    ctx.fillStyle = C.body; ctx.strokeStyle = C.ink; ctx.lineWidth = 1.5; ctx.beginPath();
    [0, 1, 2, 5, 4, 3].forEach((i, k) => { const q = P(...HX.LEGS[i].m); k ? ctx.lineTo(q[0], q[1]) : ctx.moveTo(q[0], q[1]); }); ctx.closePath(); ctx.fill(); ctx.stroke();
    seg(ctx, P(0, 0), P(55, 0), C.ink, 2);
    feet.forEach((f, i) => {
      const q = P(f.x, f.y);
      if (f.st) { dot(ctx, q, 8, C.ink); dot(ctx, q, 6, HX.COLORS[i]); }
      else { ctx.fillStyle = C.paper; ctx.strokeStyle = HX.COLORS[i]; ctx.lineWidth = 3; ctx.beginPath(); ctx.arc(q[0], q[1], 11, 0, 7); ctx.fill(); ctx.stroke(); }
    });
    if (m) {
      const a = P(0, 0), q = P(...m.q), L = Math.hypot(q[0] - a[0], q[1] - a[1]) || 1, ux = (q[0] - a[0]) / L, uy = (q[1] - a[1]) / L;
      seg(ctx, a, q, C.blue, 3);
      const txt = `${t('g_margin')} ${m.d.toFixed(0)} mm`, al = ux > 0.3 ? 'left' : (ux < -0.3 ? 'right' : 'center'), lp = [q[0] + ux * 16, q[1] + uy * 16 + 4];
      ctx.font = '12.5px "JetBrains Mono", monospace'; const tw = ctx.measureText(txt).width, x0b = al === 'left' ? lp[0] : (al === 'right' ? lp[0] - tw : lp[0] - tw / 2);
      ctx.fillStyle = C.paper; ctx.globalAlpha = 0.9; ctx.fillRect(x0b - 4, lp[1] - 13, tw + 8, 18); ctx.globalAlpha = 1;
      label(ctx, txt, lp, C.blue, 12.5, al);
    }
    dot(ctx, P(0, 0), 6, C.bad); label(ctx, t('g_com'), [ox, oy + 42], C.bad, 11.5, 'center');

    // readout tiles
    const S = vTop(gait) * b * CFG[gait].T, tile = (k, v) => `<div><span class="k">${k}</span>${v}</div>`;
    $('gkv').innerHTML = [tile(t('k_beta'), BETA_TXT[gait]), tile(t('k_down'), down), tile(t('k_T'), `${CFG[gait].T} s`), tile(t('k_vtop'), `${vTop(gait).toFixed(0)} mm/s`),
      tile(t('k_S'), `${S.toFixed(0)} mm`), tile(t('k_margin'), `${m ? m.d.toFixed(0) : '–'} / ${worst[gait].toFixed(0)} mm`)].join('');
    gtIn.value = gt; gtOut.textContent = gt.toFixed(2);
  }
  function gaitLoop(now) {
    if (!gOn || !gplay) return;
    const el = Math.min(0.1, (now - gLast) / 1000); gLast = now;
    gt = (gt + el / CFG[gait].T) % 2; drawGait(); requestAnimationFrame(gaitLoop);
  }
  const startGait = () => { if (gOn && gplay) { gLast = performance.now(); requestAnimationFrame(gaitLoop); } };
  const setPlay = p => { gplay = p; $('gplay').setAttribute('aria-pressed', String(p)); $('gplay').innerHTML = t(p ? 'bPause' : 'bPlay'); startGait(); };
  $('gplay').addEventListener('click', () => setPlay(!gplay));
  gtIn.addEventListener('input', () => { setPlay(false); gt = +gtIn.value; drawGait(); });
  $('gaitSeg').querySelectorAll('button').forEach(bt => bt.addEventListener('click', () => {
    gait = bt.dataset.g; $('gaitSeg').querySelectorAll('button').forEach(x => x.setAttribute('aria-pressed', String(x === bt))); drawGait();
  }));
  new IntersectionObserver(es => es.forEach(e => { const w = gOn; gOn = e.isIntersecting; if (gOn && !w) startGait(); })).observe(gc);

  /* ---------- 2. the walker, a port of our Walker class ---------- */
  class Walker {
    constructor() {
      this.p0 = HOME.map(f => f.slice()); this.p = HOME.map(f => f.slice()); this.lift = HOME.map(f => f.slice());
      this.was = Array(6).fill(true); this.idleTime = 0.3; this.idle = 0; this.stopped = true;
      this.settled = Array(6).fill(false); this.hold = Array(6).fill(false);
      this.t = 0; this.gait = 'tripod'; this.T = CFG.tripod.T; this.beta = GAITS.tripod[0]; this.startHold();
    }
    setGait(g) {
      if (!this.stopped) return false;
      this.gait = g; this.T = CFG[g].T; this.beta = GAITS[g][0];
      this.t = (GAITS[g][1][0] + this.beta) * this.T; // start where R1 begins its swing
      this.startHold(); return true;
    }
    startHold() { // first swing starts at s = 0; other mid-swing legs wait on the ground
      const sw = [0, 1, 2, 3, 4, 5].map(i => legPhase(i, this.t, this.T, this.gait)).filter(p => !p[0]).map(p => p[1]);
      if (sw.length) this.t -= Math.min(...sw) * (1 - this.beta) * this.T;
      const one = 0.02 / ((1 - this.beta) * this.T);
      for (let i = 0; i < 6; i++) { const [st, s] = legPhase(i, this.t, this.T, this.gait); this.hold[i] = !st && s > one; }
    }
    step(vx, vy, w, dt) { // returns true if the feet moved this frame
      const moving = Math.abs(vx) > 0.5 || Math.abs(vy) > 0.5 || Math.abs(w) > 0.2;
      if (moving) {
        this.idle = 0;
        if (this.stopped) { this.stopped = false; this.startHold(); }
        else if (this.settled.some(Boolean)) for (let i = 0; i < 6; i++) if (this.settled[i]) this.hold[i] = this.hold[i] || !legPhase(i, this.t, this.T, this.gait)[0];
        this.settled.fill(false);
      } else this.idle += dt;
      if (this.stopped) return false;
      const settling = this.idle >= this.idleTime, wr = w * D2R, k = this.beta * this.T / 2;
      for (let i = 0; i < 6; i++) {
        let [st, s] = legPhase(i, this.t, this.T, this.gait);
        if (this.hold[i]) { if (st) this.hold[i] = false; else st = true; }
        if (settling && this.settled[i]) st = true;
        const [x0, y0, z0] = this.p0[i], p = this.p[i];
        if (st) {
          if (settling && !this.was[i]) this.settled[i] = true;
          const xc = p[0], yc = p[1];
          p[0] = xc - (vx - wr * yc) * dt; p[1] = yc - (vy + wr * xc) * dt; p[2] = z0;
        } else {
          if (this.was[i]) this.lift[i] = p.slice();
          const ax = x0 + k * (vx - wr * y0), ay = y0 + k * (vy + wr * x0), c = cyc(s), L = this.lift[i];
          p[0] = L[0] + c * (ax - L[0]); p[1] = L[1] + c * (ay - L[1]); p[2] = z0 + H_LIFT * (1 - Math.cos(2 * Math.PI * s)) / 2;
        }
        this.was[i] = st;
      }
      this.t += dt;
      if (settling && this.settled.every(Boolean)) { this.stopped = true; this.p.forEach((p, i) => { p[2] = this.p0[i][2]; }); this.was.fill(true); }
      return true;
    }
  }
  const legIK = p => p.map((q, i) => { const l = HX.LEGS[i], dx = q[0] - l.m[0], dy = q[1] - l.m[1], ca = Math.cos(l.a * D2R), sa = Math.sin(l.a * D2R); return HX.ik(ca * dx + sa * dy, -sa * dx + ca * dy, q[2]); });

  const wc = $('walk'), wx = wc.getContext('2d'), pad = $('pad'), px = pad.getContext('2d');
  let walker, wg, pending, cmd, bx, by, yaw, prints, dist, ang, fail, peaks, wOn = false, wLast = 0, acc = 0, az = -0.6, drag = null;
  const keys = new Set(), padV = [0, 0];
  let turnV = 0;
  function reset() {
    walker = new Walker(); wg = 'tripod'; pending = null; cmd = [0, 0, 0]; bx = 0; by = 0; yaw = 0; prints = []; dist = 0;
    ang = legIK(walker.p); fail = null; peaks = [];
    $('walkSeg').querySelectorAll('[data-g]').forEach(x => x.setAttribute('aria-pressed', String(x.dataset.g === wg)));
  }
  function input() {
    const k = c => keys.has(c) ? 1 : 0, cl = v => Math.max(-1, Math.min(1, v));
    return [cl(k('w') - k('s') + padV[1]), cl(k('a') - k('d') + padV[0]), cl(k('q') - k('e') + turnV)];
  }
  function tick() {
    if (pending && walker.stopped) { walker.setGait(pending); wg = pending; pending = null; }
    const [ix, iy, iw] = input(), vm = vTop(wg), wm = wTop(wg), accel = 31 / (GAITS[wg][0] * CFG[wg].T / 2);
    let c = pending ? [0, 0, 0] : [ix * vm, iy * vm, iw * wm];
    const lim = Math.hypot(c[0], c[1]) / vm + Math.abs(c[2]) / wm; if (lim > 1) c = c.map(v => v / lim);
    const stp = [accel * DT, accel * DT, accel * DT * wm / vm];
    cmd = cmd.map((v, j) => v + Math.max(-stp[j], Math.min(stp[j], c[j] - v)));
    const was = walker.was.slice(), moved = walker.step(cmd[0], cmd[1], cmd[2], DT);
    if (moved) {
      const yr = yaw * D2R; bx += (Math.cos(yr) * cmd[0] - Math.sin(yr) * cmd[1]) * DT; by += (Math.sin(yr) * cmd[0] + Math.cos(yr) * cmd[1]) * DT;
      yaw += cmd[2] * DT; dist += Math.hypot(cmd[0], cmd[1]) * DT;
      const yn = yaw * D2R;
      walker.was.forEach((s, i) => { if (s && !was[i]) { const p = walker.p[i]; prints.push([bx + Math.cos(yn) * p[0] - Math.sin(yn) * p[1], by + Math.sin(yn) * p[0] + Math.cos(yn) * p[1]]); } });
      if (prints.length > 60) prints.splice(0, prints.length - 60);
    }
    const nw = legIK(walker.p); let top = 0; fail = null;
    nw.forEach((a, i) => { if (!a) { fail = HX.LEGS[i].n; return; } if (ang[i]) a.forEach((v, j) => { top = Math.max(top, Math.abs(v - ang[i][j]) / DT); }); ang[i] = a; });
    peaks.push(top); if (peaks.length > 50) peaks.shift();
  }
  const G = 89.5, SC = 0.95, EL = 0.55, CY = 0.6;
  function drawICR(ctx, P) { // the ICR on the ground while turning
    if (Math.abs(cmd[2]) < 0.5 || walker.stopped) return;
    const w = cmd[2] * D2R, ix = -cmd[1] / w, iy = cmd[0] / w, yr = yaw * D2R;
    const gx = Math.cos(yr) * ix - Math.sin(yr) * iy, gy = Math.sin(yr) * ix + Math.cos(yr) * iy;
    if (Math.abs(gx) > 440 || Math.abs(gy) > 440) return;
    const q = P([gx, gy, -G]), o = P([0, 0, -G]);
    seg(ctx, o, q, C.bad, 1.2, [4, 4]);
    seg(ctx, [q[0] - 8, q[1] - 8], [q[0] + 8, q[1] + 8], C.bad, 3); seg(ctx, [q[0] - 8, q[1] + 8], [q[0] + 8, q[1] - 8], C.bad, 3);
    label(ctx, 'ICR', [q[0] + 12, q[1] + 16], C.bad, 13);
  }
  function drawWalk() {
    const n = prints.length;
    HX.draw(wx, wc.width, wc.height, {
      legs: [0, 1, 2, 3, 4, 5], pose: [0, 0, 0, 0, 0, yaw], angles: ang, az, el: EL, scale: SC, body: true, cy: CY, gridR: 440, gridOff: [-bx, -by],
      marks: prints.map((p, k) => [p[0] - bx, p[1] - by, -G, 0.15 + 0.55 * (k + 1) / n]).filter(m => Math.abs(m[0]) < 440 && Math.abs(m[1]) < 440),
      under: drawICR,
    }, C);
    const pk = Math.max(0, ...peaks), v = Math.hypot(cmd[0], cmd[1]);
    Site.kv($('wkv'), [
      [t('kw_gait'), `${t('b' + wg[0].toUpperCase() + wg.slice(1))} · T ${CFG[wg].T} s`],
      [t('kw_v'), `${v.toFixed(0)} mm/s (max ${vTop(wg).toFixed(0)})`],
      [t('kw_w'), `${cmd[2].toFixed(1)}°/s (max ${wTop(wg).toFixed(0)})`],
      [t('kw_j'), `${pk.toFixed(0)}°/s`],
      [t('kw_down'), String(walker.was.filter(Boolean).length)],
      [t('kw_d'), `${(dist / 10).toFixed(1)} cm`],
    ]);
    $('wst').innerHTML = pending ? Site.pill(true, t('w_wait')) : fail ? Site.pill(false, `${fail}: ${t('w_fail')}`) : Site.pill(pk <= LIMIT, pk <= LIMIT ? t('w_ok') : t('w_hi'));
  }
  function drawPad() {
    const W = pad.width, R = W / 2 - 14, c = W / 2; px.clearRect(0, 0, W, W);
    px.strokeStyle = C.line; px.lineWidth = 2; px.beginPath(); px.arc(c, c, R, 0, 7); px.stroke();
    seg(px, [c - R, c], [c + R, c], C.grid, 2); seg(px, [c, c - R], [c, c + R], C.grid, 2);
    label(px, '▲', [c, 34], C.muted, 20, 'center');
    dot(px, [c - padV[0] * R, c - padV[1] * R], 30, C.accent);
  }
  function walkLoop(now) {
    if (!wOn) return;
    acc += Math.min(0.1, (now - wLast) / 1000); wLast = now;
    let n = 0; while (acc >= DT && n < 5) { tick(); acc -= DT; n++; }
    drawWalk(); requestAnimationFrame(walkLoop);
  }
  // inputs
  addEventListener('keydown', e => {
    const k = e.key.toLowerCase(); if (!wOn || k.length !== 1 || !'wasdqe'.includes(k) || e.target.closest('input, textarea, select') || e.metaKey || e.ctrlKey) return;
    keys.add(k); e.preventDefault();
  });
  addEventListener('keyup', e => keys.delete(e.key.toLowerCase()));
  addEventListener('blur', () => keys.clear());
  const padAt = e => { const r = pad.getBoundingClientRect(), R = r.width / 2 - 14 * r.width / pad.width; let x = (r.left + r.width / 2 - e.clientX) / R, y = (r.top + r.height / 2 - e.clientY) / R; const n = Math.hypot(x, y); if (n > 1) { x /= n; y /= n; } padV[0] = x; padV[1] = y; drawPad(); };
  let padDrag = false;
  pad.addEventListener('pointerdown', e => { padDrag = true; pad.setPointerCapture(e.pointerId); padAt(e); });
  pad.addEventListener('pointermove', e => { if (padDrag) padAt(e); });
  const padEnd = () => { padDrag = false; padV[0] = 0; padV[1] = 0; drawPad(); };
  pad.addEventListener('pointerup', padEnd); pad.addEventListener('pointercancel', padEnd);
  const turn = $('turn');
  turn.addEventListener('input', () => { turnV = -turn.value; });
  const turnEnd = () => { turn.value = 0; turnV = 0; };
  ['pointerup', 'pointercancel', 'touchend', 'change'].forEach(ev => turn.addEventListener(ev, turnEnd));
  wc.addEventListener('pointerdown', e => { drag = e.clientX; wc.setPointerCapture(e.pointerId); wc.focus({ preventScroll: true }); });
  wc.addEventListener('pointermove', e => { if (drag != null) { az += (e.clientX - drag) * 0.01; drag = e.clientX; } });
  wc.addEventListener('pointerup', () => { drag = null; });
  $('walkSeg').querySelectorAll('[data-g]').forEach(bt => bt.addEventListener('click', () => {
    const g = bt.dataset.g; if (g === wg && !pending) return;
    if (walker.stopped) { walker.setGait(g); wg = g; pending = null; } else pending = g;
    $('walkSeg').querySelectorAll('[data-g]').forEach(x => x.setAttribute('aria-pressed', String(x.dataset.g === g)));
  }));
  $('wreset').addEventListener('click', () => { reset(); drawWalk(); });
  new IntersectionObserver(es => es.forEach(e => { const w = wOn; wOn = e.isIntersecting; if (wOn && !w) { wLast = performance.now(); requestAnimationFrame(walkLoop); } else if (!wOn) keys.clear(); })).observe(wc);

  reset();
  const all = () => { drawGait(); drawWalk(); drawPad(); $('gplay').innerHTML = t(gplay ? 'bPause' : 'bPlay'); };
  Site.onLang(all); Site.onTheme(all);
  let rz; addEventListener('resize', () => { clearTimeout(rz); rz = setTimeout(drawGait, 150); });
  all();
})();
