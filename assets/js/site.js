/* Anymoon — site */
(function () {
  const $ = (s, r) => (r || document).querySelector(s), $$ = (s, r) => [...(r || document).querySelectorAll(s)];
  const D = window.DADOS, V = '?v=1';
  const reduz = matchMedia('(prefers-reduced-motion: reduce)').matches;
  const celular = () => innerWidth < 861;

  /* ---------------- barra e menu ---------------- */
  const topo = $('#topo'), menu = $('#menu'), mbt = $('.menu-bt');
  const rola = () => topo.classList.toggle('rolou', scrollY > 10);
  addEventListener('scroll', rola, { passive: true }); rola();
  function menuAbre(v) {
    menu.hidden = !v; mbt.setAttribute('aria-expanded', v); mbt.setAttribute('aria-label', v ? 'Fechar menu' : 'Abrir menu');
    document.documentElement.style.overflow = v ? 'hidden' : '';
    if (v) topo.classList.add('rolou'); else rola();
  }
  mbt.addEventListener('click', () => menuAbre(menu.hidden));
  $$('a', menu).forEach(a => a.addEventListener('click', () => menuAbre(false)));
  addEventListener('keydown', e => { if (e.key === 'Escape' && !menu.hidden) menuAbre(false); });
  addEventListener('resize', () => { if (innerWidth > 980 && !menu.hidden) menuAbre(false); });

  /* ---------------- hero: o retrato se pinta ---------------- */
  const hero = $('.hero'), cv = $('#pintura');
  const VW = 1080, VH = 1920;
  function geo(W, H) {
    const larga = W / H > 1.05 && W >= 700;
    if (larga) {
      const top = 64, faixa = Math.max(118, H * .165), s = Math.min(H - top - faixa - 6, W * .42);
      return { larga, s, x: (W - s) / 2, y: top + (H - top - faixa - s) / 2 + 3 };
    }
    const s = Math.min(W * .92, H * .43);
    return { larga, s, x: (W - s) / 2, y: H * .5 - s / 2 };
  }
  let modo = 'shader', T = null, t0 = 0, fim = false, ret = null, video = null;
  const DUR = window.pinturaDuracao || 4.9;
  function medidas() {
    const W = hero.clientWidth, H = hero.clientHeight;
    let g = geo(W, H);
    if (modo === 'video') {
      const gv = geo(VW, VH), k = Math.max(W / VW, H / VH), ox = (W - VW * k) / 2, oy = (H - VH * k) / 2;
      g = { larga: false, s: gv.s * k, x: ox + gv.x * k, y: oy + gv.y * k };
    }
    ret = g;
    const lado = parseFloat(getComputedStyle(document.documentElement).getPropertyValue('--lado')) || 18;
    const gap = Math.max(18, g.s * .035);
    const nome = g.larga ? Math.min((g.x - gap - lado) / 2.45, g.s * .27, 210) : Math.min((W - 2 * lado) / 4.55, (g.y - 64) * .6, 96);
    const st = hero.style;
    st.setProperty('--ax', g.x + 'px'); st.setProperty('--ay', g.y + 'px'); st.setProperty('--as', g.s + 'px');
    st.setProperty('--gap', gap + 'px'); st.setProperty('--nome', nome + 'px');
    hero.classList.toggle('pe', !g.larga);
    hero.classList.toggle('baixo', !g.larga && H < 700);
    return { W, H };
  }
  const papel = [238, 231, 219];
  function quadro(t) {
    const { W, H } = medidas();
    T.quadro(t, W, H, Math.min(2, devicePixelRatio || 1), [ret.x, ret.y, ret.s], null);
  }
  function pronto() { hero.classList.add('pronto'); }
  function loop(now) {
    const t = (now - t0) / 1000;
    if (t > .9) pronto();
    quadro(Math.min(t, DUR + .1));
    if (t < DUR + .1) requestAnimationFrame(loop); else fim = true;
  }
  function imagemFinal() {
    modo = 'final'; cv.remove();
    const im = new Image(); im.className = 'final'; im.alt = ''; im.src = 'assets/hero/final.webp' + V; hero.prepend(im);
    medidas(); pronto();
  }
  async function iniciaShader() {
    modo = 'shader';
    T = window.pinturaHero && window.pinturaHero(cv);
    if (!T || !T.ok) return imagemFinal();
    try {
      const [buf, meta, foto] = await Promise.all([
        fetch('assets/hero/pinceladas.bin' + V).then(r => r.arrayBuffer()),
        fetch('assets/hero/pinceladas.json' + V).then(r => r.json()),
        new Promise((ok, erro) => { const m = new Image(); m.onload = () => ok(m); m.onerror = erro; m.src = 'assets/hero/retrato.webp' + V; })
      ]);
      T.carregar(buf, meta, foto);
      if (document.fonts) await Promise.race([document.fonts.ready, new Promise(r => setTimeout(r, 900))]);
      if (reduz) { fim = true; quadro(99); pronto(); return; }
      t0 = performance.now(); requestAnimationFrame(loop);
    } catch (e) { imagemFinal(); }
  }
  function iniciaVideo() {
    modo = 'video'; cv.style.display = 'none';
    video = document.createElement('video');
    Object.assign(video, { muted: true, playsInline: true, preload: 'auto', autoplay: true });
    video.setAttribute('muted', ''); video.setAttribute('playsinline', ''); video.setAttribute('aria-hidden', 'true');
    video.src = 'assets/video/hero-pe.mp4' + V; hero.prepend(video); medidas();
    let saiu = false;
    const desiste = () => { if (saiu) return; saiu = true; video.remove(); video = null; cv.style.display = ''; iniciaShader(); };
    const p = video.play();
    if (p && p.catch) p.catch(desiste);
    video.addEventListener('error', desiste);
    video.addEventListener('playing', () => setTimeout(pronto, 700), { once: true });
    setTimeout(() => { if (video && video.paused && !saiu && video.currentTime === 0) desiste(); }, 2600);
  }
  const W0 = innerWidth, H0 = innerHeight;
  if (matchMedia('(pointer:coarse)').matches && W0 / H0 < .62 && !reduz) iniciaVideo(); else iniciaShader();
  medidas();
  let rz = 0;
  addEventListener('resize', () => {
    cancelAnimationFrame(rz);
    rz = requestAnimationFrame(() => {
      if (modo === 'video' && innerWidth / innerHeight >= .62 && video) { video.remove(); video = null; cv.style.display = ''; iniciaShader(); return; }
      if (modo === 'shader' && fim) quadro(99); else medidas();
    });
  });

  /* ---------------- formulario (usado por varios lugares) ---------------- */
  const form = $('#form');
  function marca(nome, valor) {
    const g = $(`.ops[data-nome="${nome}"]`); if (!g) return;
    $$('button', g).forEach(b => b.setAttribute('aria-pressed', b.textContent.trim() === valor));
  }
  function valor(nome) { const b = $(`.ops[data-nome="${nome}"] button[aria-pressed="true"]`); return b ? b.textContent.trim() : ''; }
  $$('.ops').forEach(g => g.addEventListener('click', e => {
    const b = e.target.closest('button'); if (!b) return;
    const on = b.getAttribute('aria-pressed') !== 'true';
    $$('button', g).forEach(x => x.setAttribute('aria-pressed', 'false'));
    if (on || g.dataset.nome === 'cidade') b.setAttribute('aria-pressed', 'true');
  }));
  function irForm(ref, tipo) {
    if (ref != null) $('#f-ref').value = ref;
    if (tipo) marca('tipo', tipo);
    $('#orcamento').scrollIntoView({ behavior: reduz ? 'auto' : 'smooth' });
  }
  $$('[data-cidade]').forEach(b => b.addEventListener('click', () => { marca('cidade', b.dataset.cidade); irForm(); }));
  form.addEventListener('submit', e => {
    e.preventDefault();
    const nome = $('#f-nome').value.trim(), ref = $('#f-ref').value.trim(), ideia = $('#f-ideia').value.trim();
    const erro = $('#f-erro');
    if (!nome || !(ref || ideia)) { erro.hidden = false; (nome ? $('#f-ideia') : $('#f-nome')).focus(); return; }
    erro.hidden = true;
    const L = ['Oi, Any! Vim pelo seu site e quero um orçamento.', '', 'Nome: ' + nome, 'Cidade: ' + (valor('cidade') || '-')];
    if (valor('tipo')) L.push('Tipo: ' + valor('tipo'));
    if (ref) L.push('Arte ou referência: ' + ref);
    if (valor('local')) L.push('Local do corpo: ' + valor('local'));
    const tam = $('#f-tam').value.trim(); if (tam) L.push('Tamanho aproximado: ' + (/cm/i.test(tam) ? tam : tam + ' cm'));
    const q = $('#f-quando').value.trim(); if (q) L.push('Quando: ' + q);
    if (ideia) L.push('', ideia);
    window.open('https://wa.me/5511983873974?text=' + encodeURIComponent(L.join('\n')), '_blank', 'noopener');
  });

  /* ---------------- lightbox ---------------- */
  const lb = $('#lb'), lbImg = $('#lb-img'), lbLeg = $('#lb-leg');
  let lista = [], idx = 0, volta = null;
  function lbMostra() {
    const it = lista[idx];
    lbImg.classList.remove('ok'); lbImg.alt = it.t;
    lbImg.onload = () => lbImg.classList.add('ok');
    lbImg.src = it.src; lbLeg.textContent = it.t;
    if (lbImg.complete && lbImg.naturalWidth) lbImg.classList.add('ok');
    const um = lista.length < 2; $('#lb-ant').hidden = um; $('#lb-prox').hidden = um;
  }
  function lbAbre(l, i, el) {
    lista = l; idx = i; volta = el; lb.hidden = false; document.documentElement.style.overflow = 'hidden'; lbMostra(); $('#lb-fechar').focus();
  }
  function lbFecha() { lb.hidden = true; document.documentElement.style.overflow = ''; if (volta) volta.focus({ preventScroll: true }); }
  const passa = d => { idx = (idx + d + lista.length) % lista.length; lbMostra(); };
  $('#lb-fechar').addEventListener('click', lbFecha);
  $('#lb-ant').addEventListener('click', () => passa(-1));
  $('#lb-prox').addEventListener('click', () => passa(1));
  lb.addEventListener('click', e => { if (e.target === lb) lbFecha(); });
  addEventListener('keydown', e => {
    if (lb.hidden) return;
    if (e.key === 'Escape') lbFecha(); else if (e.key === 'ArrowRight') passa(1); else if (e.key === 'ArrowLeft') passa(-1);
  });
  let tx = null;
  lb.addEventListener('touchstart', e => { tx = e.touches[0].clientX; }, { passive: true });
  lb.addEventListener('touchend', e => { if (tx == null) return; const d = e.changedTouches[0].clientX - tx; if (Math.abs(d) > 50 && lista.length > 1) passa(d < 0 ? 1 : -1); tx = null; });
  $('#lb-quero').addEventListener('click', () => { const it = lista[idx]; lbFecha(); irForm(it.ref, it.tipo); });

  /* ---------------- portfolio ---------------- */
  const TIPO = { obras: 'Releitura de obra de arte', jardim: 'Jardim da memória' };
  const grade = $('#grade');
  grade.innerHTML = D.pecas.map((p, i) => `<button class="peca" data-cat="${p.cat}" data-i="${i}"><span class="foto"><img src="assets/img/p/${p.id}.webp${V}" alt="${p.t}" loading="lazy" width="720" height="900"></span><span class="leg">${p.t}</span></button>`).join('');
  let cat = 'todas', todas = false;
  const limite = () => celular() ? 8 : 12;
  function filtra(anima) {
    let n = 0;
    $$('.peca', grade).forEach(el => {
      const ok = cat === 'todas' || el.dataset.cat === cat;
      const mostra = ok && (todas || cat !== 'todas' || n < limite());
      if (ok) n++;
      const era = el.hidden; el.hidden = !mostra;
      if (anima && mostra && era) { el.classList.remove('entra'); void el.offsetWidth; el.classList.add('entra'); }
    });
    $('#ver-todas').parentElement.hidden = todas || cat !== 'todas';
  }
  function filtro(c) {
    cat = c; $$('.filtros button').forEach(b => b.setAttribute('aria-pressed', b.dataset.cat === c)); filtra(true);
  }
  $$('.filtros button').forEach(b => b.addEventListener('click', () => filtro(b.dataset.cat)));
  $('#ver-todas').addEventListener('click', () => { todas = true; filtra(true); });
  $$('[data-filtro]').forEach(a => a.addEventListener('click', () => filtro(a.dataset.filtro)));
  grade.addEventListener('click', e => {
    const el = e.target.closest('.peca'); if (!el) return;
    const vis = $$('.peca', grade).filter(x => !x.hidden);
    const l = vis.map(x => { const p = D.pecas[+x.dataset.i]; return { src: `assets/img/o/${p.id}.webp${V}`, t: p.t, ref: p.t, tipo: TIPO[p.cat] || 'Uma ideia minha' }; });
    lbAbre(l, vis.indexOf(el), el);
  });
  filtra(false);
  let larguraAntes = celular();
  addEventListener('resize', () => { if (celular() !== larguraAntes) { larguraAntes = celular(); filtra(false); disp(); cicat(); } });

  /* ---------------- da tela para a pele ---------------- */
  const sel = $('#obras-sel'), pObra = $('#par-obra'), pPele = $('#par-pele');
  sel.innerHTML = D.obras.map((o, i) => `<button aria-pressed="${i === 0}" data-i="${i}" aria-label="${o.nome}, ${o.autor}"><img src="assets/img/obra/${o.id}.webp${V}" alt=""></button>`).join('');
  let obraAtual = 0;
  function trocaObra(i) {
    obraAtual = i; const o = D.obras[i];
    $$('button', sel).forEach(b => b.setAttribute('aria-pressed', +b.dataset.i === i));
    [pObra, pPele].forEach(im => im.style.opacity = 0);
    setTimeout(() => {
      pObra.src = `assets/img/obra/${o.id}.webp${V}`; pObra.alt = `${o.nome}, de ${o.autor}`; pObra.width = o.w; pObra.height = o.h;
      pPele.src = `assets/img/o/${o.peca}.webp${V}`; pPele.alt = `Releitura de ${o.nome} tatuada pela Any`;
      $('#par-leg-obra').innerHTML = `${o.nome}<small>${o.autor}</small>`;
      const vem = () => { pObra.style.opacity = 1; pPele.style.opacity = 1; };
      Promise.all([pObra, pPele].map(im => im.decode ? im.decode().catch(() => { }) : 0)).then(vem);
    }, reduz ? 0 : 260);
  }
  sel.addEventListener('click', e => { const b = e.target.closest('button'); if (b) trocaObra(+b.dataset.i); });
  trocaObra(0);
  $('[data-ref-obra]').addEventListener('click', e => { e.preventDefault(); irForm(D.obras[obraAtual].nome + ', de ' + D.obras[obraAtual].autor.split(',')[0], 'Releitura de obra de arte'); });

  /* ---------------- jardim da memoria ---------------- */
  $('#livro-bt').addEventListener('click', () => $('#livro').classList.remove('fechado'));
  const pag = $('#paginas');
  pag.innerHTML = D.jardim.map((p, i) => `<button class="pagina revela" data-i="${i}"><span class="foto"><img src="assets/img/j/${p.id}.webp${V}" alt="${p.t}, arte da coleção Jardim da memória" loading="lazy" width="540" height="960"></span><span class="leg">${p.t}</span></button>`).join('');
  pag.addEventListener('click', e => {
    const el = e.target.closest('.pagina'); if (!el) return;
    lbAbre(D.jardim.map(p => ({ src: `assets/img/jg/${p.id}.webp${V}`, t: p.t, ref: 'Jardim da memória: ' + p.t, tipo: 'Jardim da memória' })), +el.dataset.i, el);
  });

  /* ---------------- disponiveis ---------------- */
  const dEl = $('#disp'); let dTodas = false;
  dEl.innerHTML = D.disp.map((p, i) => `<button class="pagina" data-i="${i}"><span class="foto"><img src="assets/img/d/${p.id}.webp${V}" alt="${p.t}, arte disponível para tatuar" loading="lazy" width="540" height="960"></span><span class="leg">${p.t}</span></button>`).join('');
  function disp() { const lim = celular() ? 4 : 8; $$('.pagina', dEl).forEach((el, i) => el.hidden = !dTodas && i >= lim); $('#ver-disp').parentElement.hidden = dTodas; }
  $('#ver-disp').addEventListener('click', () => { dTodas = true; disp(); $$('.pagina', dEl).forEach(el => { el.classList.remove('entra'); void el.offsetWidth; el.classList.add('entra'); }); });
  dEl.addEventListener('click', e => {
    const el = e.target.closest('.pagina'); if (!el) return;
    const vis = $$('.pagina', dEl).filter(x => !x.hidden);
    lbAbre(vis.map(x => { const p = D.disp[+x.dataset.i]; return { src: `assets/img/dg/${p.id}.webp${V}`, t: p.t, ref: 'Disponível: ' + p.t, tipo: 'Uma arte disponível' }; }), vis.indexOf(el), el);
  });
  disp();

  /* ---------------- cicatrizadas ---------------- */
  const cEl = $('#cic'); let cTodas = false;
  cEl.innerHTML = D.cic.map((p, i) => `<button class="peca" data-i="${i}"><span class="foto"><img src="assets/img/c/${p.id}.webp${V}" alt="Tatuagem cicatrizada: ${p.t}" loading="lazy" width="640" height="800"></span><span class="leg">${p.t}</span></button>`).join('');
  function cicat() { const lim = celular() ? 4 : 8; $$('.peca', cEl).forEach((el, i) => el.hidden = !cTodas && i >= lim); $('#cic-mais-c').hidden = cTodas || D.cic.length <= lim; }
  $('#cic-mais').addEventListener('click', () => { cTodas = true; cicat(); });
  cEl.addEventListener('click', e => {
    const el = e.target.closest('.peca'); if (!el) return;
    const vis = $$('.peca', cEl).filter(x => !x.hidden);
    lbAbre(vis.map(x => { const p = D.cic[+x.dataset.i]; return { src: `assets/img/c/${p.id}.webp${V}`, t: p.t, ref: 'Cicatrizada: ' + p.t, tipo: '' }; }), vis.indexOf(el), el);
  });
  cicat();

  /* ---------------- loja ---------------- */
  const brl = n => 'R$ ' + n.toLocaleString('pt-BR', { minimumFractionDigits: 2 });
  $('#vitrine').innerHTML = D.loja.map(p => `<a class="prod revela" href="${p.url}" target="_blank" rel="noopener"><span class="foto"><img src="assets/img/l/${p.id}-0.webp${V}" alt="${p.nome}, ${p.linha}" loading="lazy" width="640" height="800"><img src="assets/img/l/${p.id}-1.webp${V}" alt="" loading="lazy" width="640" height="800"></span><h3>${p.nome}</h3><span class="linha">${p.linha}</span><span class="preco">${brl(p.preco)}</span><span class="bt bt-linha">Comprar</span></a>`).join('');

  /* ---------------- entradas ao rolar ---------------- */
  const els = $$('.revela');
  if ('IntersectionObserver' in window && !reduz) {
    const io = new IntersectionObserver(es => es.forEach(e => { if (e.isIntersecting) { e.target.classList.add('visto'); io.unobserve(e.target); } }), { rootMargin: '0px 0px -8% 0px' });
    els.forEach(el => { if (el.getBoundingClientRect().top < innerHeight) el.classList.add('visto'); else io.observe(el); });
  } else els.forEach(el => el.classList.add('visto'));
})();
