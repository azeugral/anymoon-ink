(() => {
  const $ = (s) => document.querySelector(s);

  // entradas suaves
  const io = new IntersectionObserver((es) => es.forEach((e) => {
    if (e.isIntersecting) { e.target.classList.add('vista'); io.unobserve(e.target); }
  }), { rootMargin: '0px 0px -8% 0px' });
  document.querySelectorAll('.revela,.entra').forEach((el) => io.observe(el));

  // da linha à cor
  const nomes = ['Esboço a lápis', 'Primeira camada', 'Os olhos e o focinho', 'O dourado do pelo', 'Sombras e volume', 'Pelo por pelo', 'Os últimos brilhos', 'Pronto'];
  const r = $('#etapa'), a = $('#etapa-img'), b = $('#etapa-prox'), nome = $('#etapa-nome');
  const pre = []; for (let i = 0; i < 8; i++) { const im = new Image(); pre.push(im); }
  let carregou = false;
  const carrega = () => { if (carregou) return; carregou = true; pre.forEach((im, i) => { im.src = 'a/img/p' + i + '.webp'; }); };
  let atual = -1;
  const mostra = (v) => {
    const i = Math.min(7, Math.floor(v)), f = v - i;
    if (i !== atual) {
      atual = i;
      a.src = 'a/img/p' + i + '.webp';
      a.alt = 'Retrato do Baruc, etapa ' + (i + 1) + ' de 8';
      b.src = 'a/img/p' + Math.min(7, i + 1) + '.webp';
    }
    b.style.opacity = i < 7 ? f.toFixed(3) : 0;
    nome.textContent = nomes[Math.round(v)];
    r.style.setProperty('--p', (v / 7 * 100) + '%');
  };
  r.addEventListener('input', () => { parado = true; carrega(); mostra(+r.value); });
  // ao entrar na tela, as etapas passam sozinhas uma vez, devagar
  let parado = false;
  new IntersectionObserver((es, o) => es.forEach((e) => {
    if (!e.isIntersecting) return;
    o.disconnect(); carrega();
    if (matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    const t0 = performance.now() + 600, dur = 9000;
    const passo = (t) => {
      if (parado) return;
      const k = Math.min(1, Math.max(0, (t - t0) / dur));
      const v = k * 7; r.value = v; mostra(v);
      if (k < 1) requestAnimationFrame(passo);
    };
    requestAnimationFrame(passo);
  }), { threshold: 0.45 }).observe($('.etapas'));
  mostra(0);

  // vídeos tocam só quando aparecem
  const vio = new IntersectionObserver((es) => es.forEach((e) => {
    const v = e.target;
    if (e.isIntersecting) {
      if (!v.src) v.src = v.dataset.src;
      const p = v.play(); if (p) p.catch(() => {});
    } else v.pause();
  }), { threshold: 0.35 });
  document.querySelectorAll('.video video').forEach((v) => vio.observe(v));

  // caixa das obras
  const itens = [...document.querySelectorAll('#obras-grade button')];
  const cx = $('#caixa'), ci = $('#caixa-img'), cl = $('#caixa-leg');
  let at = 0, origem = null;
  const abre = (i) => {
    at = (i + itens.length) % itens.length;
    const im = itens[at].querySelector('img');
    ci.src = im.src; ci.alt = im.alt;
    cl.textContent = itens[at].querySelector('b').textContent;
  };
  itens.forEach((bt, i) => bt.addEventListener('click', () => {
    origem = bt; abre(i); cx.hidden = false; document.body.style.overflow = 'hidden'; $('#caixa-fecha').focus();
  }));
  const fecha = () => { cx.hidden = true; document.body.style.overflow = ''; if (origem) origem.focus(); };
  $('#caixa-fecha').addEventListener('click', fecha);
  $('#caixa-ant').addEventListener('click', () => abre(at - 1));
  $('#caixa-prox').addEventListener('click', () => abre(at + 1));
  cx.addEventListener('click', (e) => { if (e.target === cx || e.target.tagName === 'FIGURE') fecha(); });
  addEventListener('keydown', (e) => {
    if (cx.hidden) return;
    if (e.key === 'Escape') fecha();
    if (e.key === 'ArrowLeft') abre(at - 1);
    if (e.key === 'ArrowRight') abre(at + 1);
  });
  let x0 = null;
  cx.addEventListener('touchstart', (e) => { x0 = e.touches[0].clientX; }, { passive: true });
  cx.addEventListener('touchend', (e) => {
    if (x0 === null) return; const d = e.changedTouches[0].clientX - x0; x0 = null;
    if (Math.abs(d) > 50) abre(at + (d < 0 ? 1 : -1));
  });
})();
