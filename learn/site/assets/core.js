/* HexPod Academy shared runtime: language switch, navigation, lazy looping clips, canvas helpers.
   Each page sets <body data-root="../" data-page="s3"> and defines PAGE_I18N = {en:{...}, zh:{...}}.
   To add a language: add a block to COMMON_I18N below and to every PAGE_I18N, plus LANG_NAMES. */
const LANG_NAMES = { en: 'English', zh: '中文' };

const STAGES = [
  { id: 'home', href: '', n: '⌂' },
  { id: 'build', href: 'build/', n: '⚙' },
  { id: 's0', href: 'stage0/', n: '0' },
  { id: 's1', href: 'stage1/', n: '1' },
  { id: 's2', href: 'stage2/', n: '2' },
  { id: 's3', href: 'stage3/', n: '3' },
  { id: 's4', href: 'stage4/', n: '4' },
  { id: 's5', href: 'stage5/', n: '5' },
  { id: 's6', href: 'stage6/', n: '6' },
  { id: 's7', n: '7', soon: true },
  { id: 's8', n: '8', soon: true },
  { id: 's9', n: '9', soon: true },
];

const COMMON_I18N = {
  en: {
    langLabel: 'Language',
    n_home: 'Home', n_build: 'Build the robot', n_s0: 'Servos & power', n_s1: 'Forward kinematics', n_s2: 'Calibration',
    n_s3: 'Inverse kinematics', n_s4: 'Jacobian & forces', n_s5: 'Body kinematics', n_s6: 'Walking gaits',
    n_s7: 'Real-time on ESP32', n_s8: 'Closing the loop', n_s9: 'Simulation & learning',
    stage: 'Stage', soon: 'coming soon',
    workedT: 'Worked example', trapT: 'Common mix-up', robotT: 'Have the robot?',
    predictBtn: 'Show the answer',
    nbSoon: 'Practice notebook: coming soon',
    nbSoonNote: 'The exercises below are planned for this stage\'s notebook. Stage 3 shows what the finished version looks like.',
    seeS3: 'See the Stage 3 notebook →',
    fromBuild: 'From our build',
    credOurs: 'our build', credRk: 'rookidroid/hexapod · GPL-3.0', credPD: 'public domain · Wikimedia Commons', credWM: 'Wikimedia Commons · see file page for author & license',
    footNote: 'Hardware design: <a href="https://github.com/rookidroid/hexapod">rookidroid/hexapod</a> (Macaroon, GPL-3.0); images marked “rookidroid” come from that repository. Everything else (math, code, photos and videos marked “our build”) is from building this robot from scratch.',
    clipPlay: 'Play', clipPause: 'Pause',
  },
  zh: {
    langLabel: '语言',
    n_home: '首页', n_build: '组装机器人', n_s0: '舵机与电源', n_s1: '正运动学', n_s2: '标定',
    n_s3: '逆运动学', n_s4: 'Jacobian 与受力', n_s5: '机身运动学', n_s6: '步态',
    n_s7: 'ESP32 实时控制', n_s8: '闭环控制', n_s9: '仿真与学习',
    stage: '阶段', soon: '即将推出',
    workedT: '算一个例子', trapT: '容易搞混', robotT: '有实机的话',
    predictBtn: '看答案',
    nbSoon: '练习 notebook：即将推出',
    nbSoonNote: '下面是这一阶段 notebook 计划包含的练习。做好的样子可以先看阶段 3。',
    seeS3: '看阶段 3 的 notebook →',
    fromBuild: '我们踩过的坑',
    credOurs: '我们的实机', credRk: 'rookidroid/hexapod · GPL-3.0', credPD: '公有领域 · Wikimedia Commons', credWM: 'Wikimedia Commons · 作者与许可见文件页',
    footNote: '硬件设计：<a href="https://github.com/rookidroid/hexapod">rookidroid/hexapod</a>（Macaroon，GPL-3.0），标注“rookidroid”的图片来自该仓库。其余内容（数学、代码，以及标注“我们的实机”的照片和视频）都来自从零做这台机器人的过程。',
    clipPlay: '播放', clipPause: '暂停',
  },
};

const Site = (() => {
  const body = document.body, ROOT = body.dataset.root || '', PAGE = body.dataset.page || '';
  const hooks = [];
  let lang = 'en';
  try {
    const q = new URLSearchParams(location.search).get('lang'), s = localStorage.getItem('hexpod-lang');
    lang = (q && COMMON_I18N[q]) ? q : (s && COMMON_I18N[s]) ? s : 'en';
  } catch (e) { }
  const dict = l => Object.assign({}, COMMON_I18N[l] || {}, (typeof PAGE_I18N !== 'undefined' && PAGE_I18N[l]) || {});
  let D = dict(lang), EN = dict('en');
  const t = k => (D[k] != null ? D[k] : (EN[k] != null ? EN[k] : k));

  /* top bar, strip and pager are generated so every page stays in sync */
  function chrome() {
    const bar = document.querySelector('.bar .in');
    if (bar) {
      bar.innerHTML = `<a class="brand" href="${ROOT}index.html">HexPod <span>Academy</span></a>
        <div class="crumb" data-i18n="crumb"></div>
        <label class="lang"><span class="lbl" data-i18n="langLabel"></span><select id="lang" aria-label="Language"></select></label>`;
      const sel = document.getElementById('lang');
      Object.keys(COMMON_I18N).forEach(k => { const o = document.createElement('option'); o.value = k; o.textContent = LANG_NAMES[k] || k; sel.appendChild(o); });
      sel.addEventListener('change', () => setLang(sel.value));
    }
    const strip = document.getElementById('strip');
    if (strip) strip.innerHTML = STAGES.map(s => {
      const cls = s.id === PAGE ? 'now' : (s.soon ? 'soon' : '');
      const inner = `${s.n}<i class="nm" data-i18n="n_${s.id}"></i>`;
      return s.soon ? `<span class="${cls}" data-i18n-title="n_${s.id}">${inner}</span>` : `<a class="${cls}" href="${ROOT}${s.href}index.html" data-i18n-title="n_${s.id}">${inner}</a>`;
    }).join('');
    const pager = document.getElementById('pager');
    if (pager) {
      const live = STAGES.filter(s => !s.soon), i = live.findIndex(s => s.id === PAGE);
      const prev = live[i - 1], next = live[i + 1];
      const lab = s => (/^s\d/.test(s.id) ? `<span data-i18n="stage"></span> ${s.n} · ` : '') + `<span data-i18n="n_${s.id}"></span>`;
      pager.innerHTML = (prev ? `<a href="${ROOT}${prev.href}index.html">← ${lab(prev)}</a>` : '<span></span>') +
        (next ? `<a href="${ROOT}${next.href}index.html">${lab(next)} →</a>` : `<span class="mono" style="color:var(--muted)">7 · 8 · 9 — <span data-i18n="soon"></span></span>`);
    }
    const foot = document.getElementById('sitefoot');
    if (foot) foot.innerHTML = '<p data-i18n="footNote"></p>';
  }

  function apply() {
    D = dict(lang);
    document.documentElement.lang = lang === 'zh' ? 'zh-CN' : lang;
    const sel = document.getElementById('lang'); if (sel) sel.value = lang;
    document.querySelectorAll('[data-i18n]').forEach(el => { el.innerHTML = t(el.dataset.i18n); });
    document.querySelectorAll('[data-i18n-alt]').forEach(el => { el.alt = t(el.dataset.i18nAlt); });
    document.querySelectorAll('[data-i18n-title]').forEach(el => { el.title = t(el.dataset.i18nTitle); });
    document.querySelectorAll('[data-i18n-aria]').forEach(el => { el.setAttribute('aria-label', t(el.dataset.i18nAria)); });
    if (D.title) document.title = D.title;
    document.querySelectorAll('a[data-keep-lang]').forEach(a => { const u = a.getAttribute('href').split('?')[0]; a.setAttribute('href', u + '?lang=' + lang); });
    hooks.forEach(f => f(lang));
  }
  function setLang(l) { lang = l; try { localStorage.setItem('hexpod-lang', l); } catch (e) { } apply(); }

  /* predict boxes: <div class="predict"> … <button class="reveal"> … <div class="answer" hidden> */
  function predicts() {
    document.querySelectorAll('.predict').forEach(p => {
      const b = p.querySelector('.reveal'), a = p.querySelector('.answer');
      if (b && a) b.addEventListener('click', () => { a.hidden = false; b.hidden = true; });
    });
  }

  /* looping clips behave like GIFs: load + play only while on screen; reduced-motion users get controls instead */
  function clips() {
    const reduce = matchMedia('(prefers-reduced-motion: reduce)').matches;
    const vids = [...document.querySelectorAll('video.clip')];
    vids.forEach(v => { v.muted = true; v.loop = true; v.playsInline = true; v.setAttribute('playsinline', ''); v.preload = 'none'; if (reduce) v.controls = true; });
    if (!('IntersectionObserver' in window)) { vids.forEach(v => { v.src = v.dataset.src; if (!reduce) v.play().catch(() => { }); }); return; }
    const io = new IntersectionObserver(es => es.forEach(e => {
      const v = e.target;
      if (e.isIntersecting) { if (!v.src) v.src = v.dataset.src; if (!reduce) v.play().catch(() => { }); }
      else if (!v.paused) v.pause();
    }), { rootMargin: '200px 0px' });
    vids.forEach(v => io.observe(v));
  }

  /* external images that may fail to load: hide the whole figure instead of showing a broken icon */
  function guards() {
    document.querySelectorAll('img[data-ext], video[data-ext]').forEach(el => {
      el.addEventListener('error', () => { const f = el.closest('figure'); if (f) f.hidden = true; }, true);
    });
  }

  /* colors from CSS tokens, refreshed when the theme changes */
  const css = n => getComputedStyle(document.documentElement).getPropertyValue(n).trim();
  const colors = () => ({ ink: css('--ink'), muted: css('--muted'), grid: css('--grid'), line: css('--line'), accent: css('--accent'), blue: css('--blue'), blueSoft: css('--blue-soft'), good: css('--good'), bad: css('--bad'), body: css('--body'), paper: css('--paper'), accentSoft: css('--accent-soft') });
  const C = colors();
  const themeHooks = [];
  const recolor = () => { Object.assign(C, colors()); themeHooks.forEach(f => f()); };
  matchMedia('(prefers-color-scheme: dark)').addEventListener('change', recolor);
  new MutationObserver(recolor).observe(document.documentElement, { attributes: true, attributeFilter: ['data-theme'] });

  /* canvas helpers */
  const cv = {
    pointer(c, e) { const b = c.getBoundingClientRect(); return [(e.clientX - b.left) * c.width / b.width, (e.clientY - b.top) * c.height / b.height]; },
    dragOn(c, fn) {
      let d = false;
      c.addEventListener('pointerdown', e => { d = true; c.setPointerCapture(e.pointerId); fn(cv.pointer(c, e), 'down'); });
      c.addEventListener('pointermove', e => { if (d) fn(cv.pointer(c, e), 'move'); });
      c.addEventListener('pointerup', () => d = false); c.addEventListener('pointercancel', () => d = false);
    },
    grid(ctx, W, H, ox, oy, s, step) {
      ctx.strokeStyle = C.grid; ctx.lineWidth = 1;
      for (let x = ((ox % (step * s)) + step * s) % (step * s); x < W; x += step * s) { ctx.beginPath(); ctx.moveTo(x, 0); ctx.lineTo(x, H); ctx.stroke(); }
      for (let y = ((oy % (step * s)) + step * s) % (step * s); y < H; y += step * s) { ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(W, y); ctx.stroke(); }
    },
    seg(ctx, a, b, color, w, dash) { ctx.strokeStyle = color; ctx.lineWidth = w; ctx.lineCap = 'round'; ctx.setLineDash(dash || []); ctx.beginPath(); ctx.moveTo(a[0], a[1]); ctx.lineTo(b[0], b[1]); ctx.stroke(); ctx.setLineDash([]); },
    dot(ctx, p, r, color) { ctx.fillStyle = color; ctx.beginPath(); ctx.arc(p[0], p[1], r, 0, 7); ctx.fill(); },
    label(ctx, txt, p, color, size, align) { ctx.fillStyle = color || C.ink; ctx.font = `${size || 15}px "JetBrains Mono", monospace`; ctx.textAlign = align || 'left'; ctx.fillText(txt, p[0], p[1]); ctx.textAlign = 'left'; },
    arrow(ctx, a, b, color, w) {
      const ang = Math.atan2(b[1] - a[1], b[0] - a[0]), h = 9 + (w || 2) * 1.5;
      cv.seg(ctx, a, b, color, w || 2);
      ctx.fillStyle = color; ctx.beginPath(); ctx.moveTo(b[0], b[1]);
      ctx.lineTo(b[0] - h * Math.cos(ang - 0.4), b[1] - h * Math.sin(ang - 0.4)); ctx.lineTo(b[0] - h * Math.cos(ang + 0.4), b[1] - h * Math.sin(ang + 0.4)); ctx.closePath(); ctx.fill();
    },
    cross(ctx, p, color) { ctx.strokeStyle = color; ctx.lineWidth = 2; ctx.beginPath(); ctx.arc(p[0], p[1], 10, 0, 7); ctx.moveTo(p[0] - 16, p[1]); ctx.lineTo(p[0] + 16, p[1]); ctx.moveTo(p[0], p[1] - 16); ctx.lineTo(p[0], p[1] + 16); ctx.stroke(); },
  };
  const kv = (el, rows) => { el.innerHTML = rows.map(([k, v]) => `<dt>${k}</dt><dd>${v}</dd>`).join(''); };
  const pill = (ok, txt) => `<span class="pill ${ok ? 'ok' : 'no'}">${txt}</span>`;
  /* slider rows: <div class="ctl"><label>θ1</label><input type=range …><output></output></div> */
  function slider(input, fmt, fn) {
    const out = input.parentElement.querySelector('output');
    const upd = () => { if (out) out.textContent = fmt ? fmt(+input.value) : input.value; fn && fn(+input.value); };
    input.addEventListener('input', upd); upd();
    return upd;
  }
  const reduceMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;

  chrome(); predicts(); guards();
  document.addEventListener('DOMContentLoaded', () => { });
  apply(); clips();
  return { t, get lang() { return lang; }, onLang(f) { hooks.push(f); }, onTheme(f) { themeHooks.push(f); }, C, cv, kv, pill, slider, ROOT, reduceMotion, D2R: Math.PI / 180 };
})();
