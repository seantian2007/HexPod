(() => {
  const $ = id => document.getElementById(id);
  const C = Site.C, t = Site.t, { seg, dot, label } = Site.cv, D2R = Site.D2R;
  const A = 0.0901, DEAD = 8, SPEED = 200; // °/µs, deadband µs, no-load °/s (all measured on our servo)

  /* ---------- pulse → angle widget ---------- */
  const cv = $('pulse'), ctx = cv.getContext('2d');
  let us = 1500, held = 1500, actual = 0, last = performance.now(), on = false, running = false;
  const inp = $('us');
  const set = v => { us = Math.max(500, Math.min(2500, Math.round(v))); inp.value = us; inp.dispatchEvent(new Event('input')); };
  [['m1', -1], ['p1', 1], ['m10', -10], ['p10', 10]].forEach(([id, d]) => $(id).addEventListener('click', () => set(us + d)));
  Site.slider(inp, v => `${v}`, v => { us = v; if (Math.abs(us - held) > DEAD) held = us; kick(); });

  function draw(now) {
    const dt = Math.min(0.05, (now - last) / 1000); last = now;
    const target = A * (held - 1500);
    const step = SPEED * dt;
    actual += Math.max(-step, Math.min(step, target - actual));
    if (Site.reduceMotion) actual = target;
    const W = cv.width, H = cv.height; ctx.clearRect(0, 0, W, H);
    // row 1: two 20 ms frames
    const x0 = 40, x1 = W - 30, y1 = 70, hi = 34;
    label(ctx, t('w_frames'), [x0, 28], C.muted, 13);
    const ms = (x1 - x0) / 40;
    ctx.strokeStyle = C.ink; ctx.lineWidth = 2; ctx.beginPath(); ctx.moveTo(x0, y1);
    [0, 20].forEach(f => { const a = x0 + f * ms, b = a + us / 1000 * ms; ctx.lineTo(a, y1); ctx.lineTo(a, y1 - hi); ctx.lineTo(b, y1 - hi); ctx.lineTo(b, y1); });
    ctx.lineTo(x1, y1); ctx.stroke();
    [0, 20, 40].forEach(f => { seg(ctx, [x0 + f * ms, y1 + 6], [x0 + f * ms, y1 + 12], C.muted, 1); label(ctx, `${f} ms`, [x0 + f * ms, y1 + 28], C.muted, 12, 'center'); });
    // row 2: zoom on the first 3 ms
    const y2 = 190, z = (x1 - x0) / 3000;
    label(ctx, t('w_zoom'), [x0, 120], C.muted, 13);
    ctx.fillStyle = C.blueSoft; ctx.fillRect(x0 + 500 * z, y2 - 50, 2000 * z, 50);
    label(ctx, t('w_range'), [x0 + 1500 * z, y2 - 58], C.blue, 12, 'center');
    ctx.strokeStyle = C.accent; ctx.lineWidth = 3; ctx.beginPath(); ctx.moveTo(x0, y2); ctx.lineTo(x0, y2 - 40); ctx.lineTo(x0 + us * z, y2 - 40); ctx.lineTo(x0 + us * z, y2); ctx.lineTo(x1, y2); ctx.stroke();
    [0, 500, 1000, 1500, 2000, 2500, 3000].forEach(v => { seg(ctx, [x0 + v * z, y2 + 6], [x0 + v * z, y2 + 12], C.muted, 1); label(ctx, `${v}`, [x0 + v * z, y2 + 28], C.muted, 12, 'center'); });
    label(ctx, 'µs', [x1, y2 + 46], C.muted, 12, 'right');
    label(ctx, `${us} µs`, [x0 + us * z, y2 - 46], C.accent, 15, us > 2200 ? 'right' : 'left');
    // row 3: the horn
    const cx = W / 2, cy = 470, R = 150;
    ctx.fillStyle = C.body; ctx.beginPath(); ctx.arc(cx, cy, R + 14, Math.PI, 0); ctx.closePath(); ctx.fill();
    for (let a = -90; a <= 90; a += 15) {
      const r = a * D2R, big = a % 45 === 0;
      seg(ctx, [cx + (R + 4) * Math.sin(r), cy - (R + 4) * Math.cos(r)], [cx + (R + (big ? 16 : 10)) * Math.sin(r), cy - (R + (big ? 16 : 10)) * Math.cos(r)], C.muted, big ? 2 : 1);
      if (big) label(ctx, `${a > 0 ? '+' : ''}${a}°`, [cx + (R + 34) * Math.sin(r), cy - (R + 34) * Math.cos(r) + 4], C.muted, 12, 'center');
    }
    const tr = target * D2R, ar = actual * D2R;
    seg(ctx, [cx, cy], [cx + R * Math.sin(tr), cy - R * Math.cos(tr)], C.accent, 2, [6, 5]);
    seg(ctx, [cx, cy], [cx + (R - 12) * Math.sin(ar), cy - (R - 12) * Math.cos(ar)], C.ink, 12);
    dot(ctx, [cx, cy], 16, C.ink); dot(ctx, [cx, cy], 6, C.paper);
    label(ctx, t('w_cmd'), [24, cy - 30], C.accent, 13); label(ctx, t('w_act'), [24, cy - 10], C.ink, 13);
    Site.kv($('pkv'), [[t('w_pw'), `${us} µs`], ['ticks', `${Math.round(us / (20000 / 4096))}`], [t('w_cmdA'), `${(A * (us - 1500)).toFixed(1)}°`], [t('w_actA'), `${actual.toFixed(1)}°`]]);
    $('pst').innerHTML = us !== held ? Site.pill(false, t('w_dead')) : Site.pill(true, t('w_moving'));
    if (on && !Site.reduceMotion && Math.abs(target - actual) > 0.01) requestAnimationFrame(draw); else running = false;
  }
  function kick() { if (!running) { running = true; last = performance.now(); requestAnimationFrame(draw); } }
  new IntersectionObserver(es => es.forEach(e => { on = e.isIntersecting; if (on) kick(); })).observe(cv);
  const redraw = () => { running = true; draw(performance.now()); };
  Site.onLang(redraw); Site.onTheme(redraw);
  redraw();
})();
