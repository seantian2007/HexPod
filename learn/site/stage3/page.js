(() => {
  const $ = id => document.getElementById(id);
  const D2R = Math.PI / 180, L1 = 62, L2 = 76, L3 = 132;
  const css = n => getComputedStyle(document.documentElement).getPropertyValue(n).trim();
  const col = () => ({ ink: css('--ink'), muted: css('--muted'), grid: css('--grid'), line: css('--line'), accent: css('--accent'), blue: css('--blue'), blueSoft: css('--blue-soft'), good: css('--good'), bad: css('--bad'), body: css('--body'), paper: css('--paper'), accentSoft: css('--accent-soft') });
  let C = col();

  /* ---------- language ---------- */
  let lang = 'en';
  try { const q = new URLSearchParams(location.search).get('lang'); const s = localStorage.getItem('hexpod-lang'); lang = (q && I18N[q]) ? q : (s && I18N[s]) ? s : 'en'; } catch (e) { }
  const sel = $('lang');
  Object.keys(I18N).forEach(k => { const o = document.createElement('option'); o.value = k; o.textContent = LANG_NAMES[k] || k; sel.appendChild(o); });
  const t = k => (I18N[lang] && I18N[lang][k] != null) ? I18N[lang][k] : (I18N.en[k] ?? k);
  function applyLang() {
    sel.value = lang; document.documentElement.lang = lang === 'zh' ? 'zh-CN' : lang;
    document.querySelectorAll('[data-i18n]').forEach(el => { el.innerHTML = t(el.dataset.i18n); });
    $('nbLink').href = 'notebook/index.html?lang=' + lang;
    drawTop(); drawSide();
  }
  sel.addEventListener('change', () => { lang = sel.value; try { localStorage.setItem('hexpod-lang', lang); } catch (e) { } applyLang(); });

  $('reveal').addEventListener('click', () => { $('answer').hidden = false; $('reveal').hidden = true; });

  /* ---------- canvas helpers ---------- */
  function pointer(cv, e) { const b = cv.getBoundingClientRect(); return [(e.clientX - b.left) * cv.width / b.width, (e.clientY - b.top) * cv.height / b.height]; }
  function dragOn(cv, fn) {
    let d = false;
    cv.addEventListener('pointerdown', e => { d = true; cv.setPointerCapture(e.pointerId); fn(pointer(cv, e)); });
    cv.addEventListener('pointermove', e => { if (d) fn(pointer(cv, e)); });
    cv.addEventListener('pointerup', () => d = false); cv.addEventListener('pointercancel', () => d = false);
  }
  function grid(ctx, W, H, ox, oy, s, step) {
    ctx.strokeStyle = C.grid; ctx.lineWidth = 1;
    for (let x = ox % (step * s); x < W; x += step * s) { ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, H); ctx.stroke(); }
    for (let y = oy % (step * s); y < H; y += step * s) { ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke(); }
  }
  function seg(ctx, a, b, color, w, dash) { ctx.strokeStyle = color; ctx.lineWidth = w; ctx.lineCap = 'round'; ctx.setLineDash(dash || []); ctx.beginPath(); ctx.moveTo(a[0], a[1]); ctx.lineTo(b[0], b[1]); ctx.stroke(); ctx.setLineDash([]); }
  function dot(ctx, p, r, color) { ctx.fillStyle = color; ctx.beginPath(); ctx.arc(p[0], p[1], r, 0, 7); ctx.fill(); }
  function label(ctx, txt, p, color, size) { ctx.fillStyle = color || C.ink; ctx.font = `${size || 15}px "JetBrains Mono", monospace`; ctx.fillText(txt, p[0], p[1]); }
  function cross(ctx, p, color) { ctx.strokeStyle = color; ctx.lineWidth = 2; ctx.beginPath(); ctx.arc(p[0], p[1], 10, 0, 7); ctx.moveTo(p[0] - 16, p[1]); ctx.lineTo(p[0] + 16, p[1]); ctx.moveTo(p[0], p[1] - 16); ctx.lineTo(p[0], p[1] + 16); ctx.stroke(); }
  const f1 = v => v.toFixed(1);
  const kv = (el, rows) => { el.innerHTML = rows.map(([k, v]) => `<dt>${k}</dt><dd>${v}</dd>`).join(''); };
  const pill = (ok, txt) => `<span class="pill ${ok ? 'ok' : 'no'}">${txt}</span>`;

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
  let az = -0.75, spin = true, t0 = performance.now(), lastX = null;
  hv.addEventListener('pointerdown', e => { lastX = e.clientX; spin = false; hv.setPointerCapture(e.pointerId); });
  hv.addEventListener('pointermove', e => { if (lastX != null) { az += (e.clientX - lastX) * 0.01; lastX = e.clientX; } });
  hv.addEventListener('pointerup', () => { lastX = null; });
  const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
  function frame(now) {
    const tt = reduce ? 0 : (now - t0) / 1000;
    if (spin && !reduce) az = -0.75 + 0.12 * tt;
    const pose = HX.danceT(tt), ang = HX.bodyIK(pose);
    HX.draw(hc, hv.width, hv.height, { legs: [0, 1, 2, 3, 4, 5], pose, angles: ang, az, el: 0.5, scale: 1.25, body: true, cy: 0.6 }, C);
    requestAnimationFrame(frame);
  }
  requestAnimationFrame(frame);

  const recolor = () => { C = col(); drawTop(); drawSide(); };
  matchMedia('(prefers-color-scheme: dark)').addEventListener('change', recolor);
  new MutationObserver(recolor).observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });
  applyLang();
})();
