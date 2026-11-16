(() => {
  const $ = id => document.getElementById(id);
  const C = Site.C, t = Site.t, { seg, dot, label, dragOn } = Site.cv, D2R = Site.D2R;
  const TOOTH = 360 / 25, A = 0.0901, DEAD = 0.7;

  /* ---------- spline + trim: coarse tooth choice, then µs₀ ---------- */
  const cv = $('spline'), ctx = cv.getContext('2d'), trim = $('trim');
  let phi = 4.9, k = 3; // spline offset of tooth 0 at 1500 µs, chosen tooth
  const coarse = () => phi + TOOTH * k;
  const finalAng = () => coarse() + A * (+trim.value - 1500);
  const CX = 360, CY = 290, R = 118;
  const dir = a => [Math.sin(a * D2R), -Math.cos(a * D2R)];
  function draw() {
    const W = cv.width, H = cv.height; ctx.clearRect(0, 0, W, H);
    // reference line
    seg(ctx, [CX, CY], [CX, 40], C.good, 2, [7, 5]); label(ctx, t('w_ref'), [CX + 10, 52], C.good, 14);
    // spline with 25 teeth (rotates with the trim, since the shaft turns)
    const shaft = A * (+trim.value - 1500);
    ctx.fillStyle = C.body; ctx.beginPath(); ctx.arc(CX, CY, R, 0, 7); ctx.fill();
    for (let i = 0; i < 25; i++) {
      const a = phi + shaft + i * TOOTH, d = dir(a), n = [-d[1], d[0]];
      const p = [CX + d[0] * R, CY + d[1] * R], q = [CX + d[0] * (R + 14), CY + d[1] * (R + 14)];
      ctx.fillStyle = i === ((k % 25) + 25) % 25 ? C.accent : C.muted;
      ctx.beginPath(); ctx.moveTo(p[0] + n[0] * 6, p[1] + n[1] * 6); ctx.lineTo(q[0] + n[0] * 3, q[1] + n[1] * 3); ctx.lineTo(q[0] - n[0] * 3, q[1] - n[1] * 3); ctx.lineTo(p[0] - n[0] * 6, p[1] - n[1] * 6); ctx.closePath(); ctx.fill();
    }
    // horn
    const f = finalAng(), d = dir(f);
    seg(ctx, [CX, CY], [CX + d[0] * 220, CY + d[1] * 220], C.ink, 16);
    dot(ctx, [CX + d[0] * 200, CY + d[1] * 200], 5, C.paper);
    dot(ctx, [CX, CY], 22, C.ink); dot(ctx, [CX, CY], 8, C.paper);
    // error arc
    const ok = Math.abs(f) < DEAD;
    ctx.strokeStyle = ok ? C.good : C.bad; ctx.lineWidth = 3; ctx.beginPath();
    ctx.arc(CX, CY, 170, -Math.PI / 2, -Math.PI / 2 + f * D2R, f < 0); ctx.stroke();
    label(ctx, `${f > 0 ? '+' : ''}${f.toFixed(1)}°`, [CX + dir(f / 2)[0] * 192, CY + dir(f / 2)[1] * 192 + 5], ok ? C.good : C.bad, 16, 'center');
    label(ctx, t('w_drag'), [20, H - 20], C.muted, 13);
    Site.kv($('spkv'), [[t('w_tooth'), `${k}`], [t('w_coarse'), `${coarse().toFixed(1)}°`], ['µs₀', `${trim.value} µs`], [t('w_final'), `${f.toFixed(2)}°`]]);
    let st;
    if (Math.abs(coarse()) > TOOTH / 2 + 0.01) st = Site.pill(false, t('w_badTooth'));
    else if (ok) st = Site.pill(true, t('w_done'));
    else st = Site.pill(false, t('w_trim'));
    $('spst').innerHTML = st;
  }
  dragOn(cv, p => {
    const a = Math.atan2(p[0] - CX, -(p[1] - CY)) / D2R - A * (+trim.value - 1500);
    k = Math.round((a - phi) / TOOTH); draw();
  });
  Site.slider(trim, v => `${v}`, draw);
  $('newServo').addEventListener('click', () => {
    phi = (Math.random() - 0.5) * TOOTH; k = Math.random() < 0.5 ? 2 : -2; trim.value = 1500; trim.dispatchEvent(new Event('input'));
  });
  Site.onLang(draw); Site.onTheme(draw);
  draw();
})();
