(() => {
  const $ = id => document.getElementById(id);
  const C = Site.C, t = Site.t;
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
    // failed legs: mark their planted foot
    const bad = [];
    ang.forEach((a, i) => { if (!a) bad.push(HX.LEGS[i].n); });
    Site.kv($('pkv'), HX.LEGS.map((l, i) => [l.n, ang[i] ? ang[i].map(v => (Math.abs(v) < 0.5 ? 0 : v).toFixed(0).padStart(4)).join(' ') + '°' : `<span style="color:var(--bad)">✗ ${t('w_fail')}</span>`]));
    if (waving && on && !Site.reduceMotion) requestAnimationFrame(draw);
  }
  ins.forEach((inp, k) => Site.slider(inp, v => `${(+v).toFixed(1)} ${units[k]}`, () => { if (!waving) draw(); }));
  $('reset').addEventListener('click', () => { stopWave(); ins.forEach(i => { i.value = 0; i.dispatchEvent(new Event('input')); }); });
  const stopWave = () => { waving = false; $('wave').setAttribute('aria-pressed', 'false'); };
  $('wave').addEventListener('click', () => {
    if (waving) { stopWave(); draw(); return; }
    waving = true; t0 = performance.now(); $('wave').setAttribute('aria-pressed', 'true'); requestAnimationFrame(draw);
  });
  ins.forEach(i => i.addEventListener('pointerdown', stopWave));
  new IntersectionObserver(es => es.forEach(e => { const w = on; on = e.isIntersecting; if (on && !w && waving) requestAnimationFrame(draw); })).observe(cv);
  Site.onLang(draw); Site.onTheme(draw);
  draw();
})();
