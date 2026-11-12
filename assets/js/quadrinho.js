// quadrinho do ateliê: a cor sobe conforme a página é lida; no fim, um "plim" discreto
(() => {
  const q = document.getElementById('quadrinho');
  if (!q) return;
  let tick = false, completo = false, timer = 0;
  const plim = () => {
    q.classList.remove('plim'); void q.offsetWidth; q.classList.add('plim');
  };
  const pinta = () => {
    tick = false;
    const max = document.documentElement.scrollHeight - innerHeight;
    const p = max > 0 ? Math.min(1, Math.max(0, scrollY / max)) : 0;
    q.style.setProperty('--q', (p * 100).toFixed(2) + '%');
    q.classList.toggle('on', scrollY > innerHeight * 0.6);
    const fim = p > 0.985;
    if (fim && !completo) {
      completo = true; q.classList.add('pronto');
      timer = setTimeout(plim, 350);
    } else if (!fim && completo && p < 0.9) {
      completo = false; q.classList.remove('pronto'); clearTimeout(timer);
    }
  };
  q.addEventListener('animationend', (e) => { if (e.target === q) q.classList.remove('plim'); });
  addEventListener('scroll', () => { if (!tick) { tick = true; requestAnimationFrame(pinta); } }, { passive: true });
  addEventListener('resize', pinta);
  pinta();
})();
