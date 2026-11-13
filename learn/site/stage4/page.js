(() => {
  const $ = id => document.getElementById(id);
  const C = Site.C, t = Site.t, { grid, seg, dot, label, arrow, dragOn } = Site.cv, D2R = Site.D2R;
  const L1 = 62, L2 = 76, L3 = 132, F = 7.2, STALL = 25; // N per foot (tripod, 2.2 kg estimate), servo kg·cm
  const NKGCM = 1 / 0.0980665; // N·m → kg·cm  (1 kg·cm = 0.0980665 N·m)

  const cv = $('jac'), ctx = cv.getContext('2d'), S = 1.3, O = [160, 230];
  let foot = [100, -89.5], mode = 'v';
  document.querySelectorAll('[data-mode]').forEach(b => b.addEventListener('click', () => {
    mode = b.dataset.mode; document.querySelectorAll('[data-mode]').forEach(x => x.setAttribute('aria-pressed', String(x === b))); draw();
  }));
  $('goStand').addEventListener('click', () => { foot = [100, -89.5]; draw(); });
  $('goStraight').addEventListener('click', () => { foot = [196, -40]; draw(); });

  function solve(u, z) { // knee-up IK in the leg plane, u measured from the femur joint
    const D = Math.hypot(u, z), c = (D * D - L2 * L2 - L3 * L3) / (2 * L2 * L3);
    if (Math.abs(c) > 1) return null;
    const t3 = Math.acos(c), t2 = Math.atan2(z, u) + Math.atan2(L3 * Math.sin(t3), L2 + L3 * Math.cos(t3));
    return [t2, t3];
  }
  function svd2(a, b, c, d) { // singular values of [[a b],[c d]]
    const s1 = a * a + b * b + c * c + d * d, det = a * d - b * c, q = Math.sqrt(Math.max(0, s1 * s1 / 4 - det * det));
    return [Math.sqrt(s1 / 2 + q), Math.sqrt(Math.max(0, s1 / 2 - q))];
  }
  function draw() {
    const W = cv.width, H = cv.height; ctx.clearRect(0, 0, W, H); grid(ctx, W, H, O[0], O[1], S, 20);
    const P = (u, z) => [O[0] + u * S, O[1] - z * S];
    seg(ctx, P(-L1, 0), P(0, 0), C.muted, 7); dot(ctx, P(-L1, 0), 5, C.muted);
    seg(ctx, P(0, 0), P(300, 0), C.muted, 1, [4, 4]);
    const sol = solve(...foot);
    if (!sol) { label(ctx, t('w_noreach'), [20, 30], C.bad, 15); $('jkv').innerHTML = ''; $('jst').innerHTML = Site.pill(false, t('w_noreach')); return; }
    const [t2, t3] = sol, a23 = t2 - t3;
    const knee = [L2 * Math.cos(t2), L2 * Math.sin(t2)], [u, z] = foot;
    const ok = Math.abs(t2 / D2R) <= 75 && t3 / D2R >= 15 && t3 / D2R <= 165;
    // Jacobian columns in the leg plane, mm per rad
    const J2 = [-z, u], J3 = [L3 * Math.sin(a23), -L3 * Math.cos(a23)];
    const sv = svd2(J2[0], J3[0], J2[1], J3[1]).map(v => v * D2R); // mm per degree
    const kappa = sv[0] / Math.max(sv[1], 1e-9);
    if (mode === 'v') {
      const k = 0.55;
      arrow(ctx, P(u, z), P(u + J2[0] * k, z + J2[1] * k), C.blue, 3); label(ctx, 'J₂', P(u + J2[0] * k + 6, z + J2[1] * k + 6), C.blue, 17);
      arrow(ctx, P(u, z), P(u + J3[0] * k, z + J3[1] * k), C.accent, 3); label(ctx, 'J₃', P(u + J3[0] * k - 24, z + J3[1] * k - 6), C.accent, 17);
      seg(ctx, P(0, 0), P(u, z), C.blue, 1.2, [3, 4]); seg(ctx, P(...knee), P(u, z), C.accent, 1.2, [3, 4]);
    } else if (mode === 'e') {
      const k = 8, e = [[1, 1], [1, -1], [-1, -1], [-1, 1]].map(([a, b]) => P(u + k * D2R * (J2[0] * a + J3[0] * b), z + k * D2R * (J2[1] * a + J3[1] * b)));
      ctx.fillStyle = C.accentSoft; ctx.strokeStyle = C.accent; ctx.lineWidth = 2; ctx.beginPath(); e.forEach((p, i) => i ? ctx.lineTo(...p) : ctx.moveTo(...p)); ctx.closePath(); ctx.fill(); ctx.stroke();
      label(ctx, t('w_err8'), [20, 30], C.accent, 14);
    } else {
      // vertical force from the ground on the foot, lever arms to each joint
      arrow(ctx, P(u, z - 70), P(u, z - 4), C.bad, 3); label(ctx, `F = ${F} N`, P(u + 6, z - 60), C.bad, 15);
      seg(ctx, P(0, z - 14), P(u, z - 14), C.blue, 3); label(ctx, `${t('w_arm')} ${u.toFixed(0)} mm`, P(u / 2, z - 30), C.blue, 14, 'center');
      seg(ctx, P(knee[0], knee[1] + 14), P(u, knee[1] + 14), C.accent, 3); label(ctx, `${(u - knee[0]).toFixed(0)} mm`, P((knee[0] + u) / 2, knee[1] + 26), C.accent, 14, 'center');
      seg(ctx, P(u, z), P(u, knee[1] + 20), C.muted, 1, [3, 4]);
    }
    seg(ctx, P(0, 0), P(...knee), ok ? C.blue : C.bad, 9); seg(ctx, P(...knee), P(u, z), ok ? C.ink : C.bad, 7);
    dot(ctx, P(0, 0), 6, C.ink); dot(ctx, P(...knee), 6, C.ink); dot(ctx, P(u, z), 7, C.accent);
    label(ctx, t('w_dragFoot'), [20, H - 18], C.muted, 13);
    // torques for a vertical load: tau = J^T F, F = (0, -F) is the force the foot pushes on the ground
    const tau2 = J2[1] * -F / 1000 * NKGCM, tau3 = J3[1] * -F / 1000 * NKGCM;
    const rows = [['θ2, θ3', `${(t2 / D2R).toFixed(1)}°, ${(t3 / D2R).toFixed(1)}°`]];
    if (mode === 'v') rows.push(['|J₂| = D', `${Math.hypot(...J2).toFixed(0)} mm/rad = ${(Math.hypot(...J2) * D2R).toFixed(2)} mm/°`], ['|J₃| = L3', `${Math.hypot(...J3).toFixed(0)} mm/rad = ${(Math.hypot(...J3) * D2R).toFixed(2)} mm/°`]);
    if (mode === 'e') rows.push([t('w_sv'), `${sv[0].toFixed(2)} / ${sv[1].toFixed(2)} mm/°`], ['κ', kappa.toFixed(1)]);
    if (mode === 't') rows.push(['τ2', `${tau2.toFixed(1)} kg·cm (${Math.abs(tau2 / STALL * 100).toFixed(0)}%)`], ['τ3', `${tau3.toFixed(1)} kg·cm (${Math.abs(tau3 / STALL * 100).toFixed(0)}%)`]);
    Site.kv($('jkv'), rows);
    let st = ok ? '' : Site.pill(false, t('w_limit'));
    if (mode === 'e' || mode === 'v') st += ' ' + Site.pill(kappa < 6, kappa < 6 ? `κ ${kappa.toFixed(1)}: ${t('w_good')}` : `κ ${kappa.toFixed(1)}: ${t('w_sing')}`);
    if (mode === 't') st += ' ' + Site.pill(Math.abs(tau2) < 0.35 * STALL, Math.abs(tau2) < 0.35 * STALL ? t('w_tauOk') : t('w_tauHi'));
    $('jst').innerHTML = st;
  }
  dragOn(cv, p => { foot = [(p[0] - O[0]) / S, (O[1] - p[1]) / S]; draw(); });
  Site.onLang(draw); Site.onTheme(draw);
  draw();
})();
