# -*- coding: utf-8 -*-
"""Auditoria: estouro, corte de texto/fonte, simetria do hero no eixo, grades e erros em 13 tamanhos + teste funcional.
Uso: python tools/auditar.py [url]"""
import sys
from urllib.parse import unquote
from playwright.sync_api import sync_playwright
sys.stdout.reconfigure(encoding='utf8')
URL = next((a for a in sys.argv[1:] if a.startswith('http')), 'http://localhost:8920/')
VPS = [(320, 568, 1), (360, 640, 1), (360, 740, 1), (390, 844, 1), (430, 932, 1), (600, 900, 1), (768, 1024, 1), (844, 390, 1),
       (1024, 768, 0), (1280, 720, 0), (1440, 900, 0), (1920, 1080, 0), (2560, 1300, 0)]
ARG = ['--use-angle=d3d11', '--ignore-gpu-blocklist', '--autoplay-policy=no-user-gesture-required']
JS = r"""
() => {
  const W = document.documentElement.clientWidth, out = [];
  if (document.documentElement.scrollWidth > W) out.push('ESTOURO pagina ' + document.documentElement.scrollWidth + '>' + W);
  document.querySelectorAll('h1 span,h2,h3,p,a,button,span,strong,blockquote,cite,li,label,dt,dd,figcaption,small').forEach(el => {
    if (el.closest('[hidden],.saltar,.menu,.lb')) return;
    const cs = getComputedStyle(el); if (cs.display === 'none' || cs.visibility === 'hidden') return;
    const r = el.getBoundingClientRect(); if (!r.width || !r.height) return;
    const nome = el.tagName + '.' + el.className + ' "' + (el.textContent || '').trim().slice(0, 26) + '"';
    if (r.right > W + 1 || r.left < -1) out.push('FORA ' + nome + ' ' + Math.round(r.left) + '-' + Math.round(r.right));
    if (el.scrollWidth > el.clientWidth + 1 && cs.display !== 'inline' && el.clientWidth > 0 && cs.overflowX !== 'auto') out.push('CORTE-X ' + nome + ' ' + el.scrollWidth + '>' + el.clientWidth);
    if (cs.overflow !== 'visible' && el.scrollHeight > el.clientHeight + 1 && el.clientHeight > 0) out.push('CORTE-Y ' + nome);
    const lh = parseFloat(cs.lineHeight), fs = parseFloat(cs.fontSize);
    if (lh && lh / fs < 1.0 && el.textContent.trim() && !el.children.length) out.push('ENTRELINHA ' + nome + ' ' + (lh / fs).toFixed(2));
  });
  const eixo = W / 2, cen = s => { const r = document.querySelector(s).getBoundingClientRect(); return (r.left + r.right) / 2; };
  document.querySelectorAll('.cab h2, .grade, .vitrine, .cidades, .form').forEach(e => { const r = e.getBoundingClientRect(); if (r.width && Math.abs((r.left + r.right) / 2 - eixo) > 1.5) out.push('EIXO ' + e.className + ' ' + ((r.left + r.right) / 2 - eixo).toFixed(1)); });
  /* hero */
  const hero = document.querySelector('.hero'), h = hero.getBoundingClientRect(), st = getComputedStyle(hero);
  const ax = parseFloat(st.getPropertyValue('--ax')), ay = parseFloat(st.getPropertyValue('--ay')), as = parseFloat(st.getPropertyValue('--as'));
  const arte = { l: ax + as * .05, r: ax + as * .95, t: ay + as * .03, b: ay + as * .95 };
  const pe = hero.classList.contains('pe');
  const bts = [...document.querySelectorAll('.hero-bts .bt')].map(b => b.getBoundingClientRect());
  bts.forEach(b => { if (b.bottom > h.bottom - 2) out.push('HERO botao cortado'); });
  if (Math.abs(bts[0].top - bts[1].top) > 1 || Math.abs(bts[0].width - bts[1].width) > 1 || Math.abs(bts[0].height - bts[1].height) > 1) out.push('HERO botoes desiguais');
  if (Math.abs((bts[0].left + bts[1].right) / 2 - eixo) > 1.5) out.push('HERO botoes fora do eixo ' + ((bts[0].left + bts[1].right) / 2 - eixo).toFixed(1));
  if (Math.abs((ax + as / 2) - eixo) > 1.5) out.push('HERO arte fora do eixo');
  const n = [...document.querySelectorAll('.ne,.nd')].map(e => e.getBoundingClientRect()), barra = document.querySelector('.topo').getBoundingClientRect().bottom;
  if (n[0].left < 0 || n[1].right > W) out.push('HERO nome cortado');
  if (Math.min(n[0].top, n[1].top) < barra - 1) out.push('HERO nome sob a barra');
  const tx = [...document.querySelectorAll('.hero-txt')].map(e => e.getBoundingClientRect()).filter(r => r.width);
  const sob = (a, b) => a.left < b.r && a.right > b.l && a.top < b.b && a.bottom > b.t;
  if (!pe) {
    if (Math.abs(n[0].top - n[1].top) > 1) out.push('HERO nome desalinhado');
    if (Math.abs((eixo - n[0].right) - (n[1].left - eixo)) > 2) out.push('HERO nome assimetrico ' + Math.round(eixo - n[0].right) + '/' + Math.round(n[1].left - eixo));
    if (tx.length === 2) { if (Math.abs(tx[0].top - tx[1].top) > 1) out.push('HERO textos desalinhados'); if (Math.abs((eixo - tx[0].right) - (tx[1].left - eixo)) > 2) out.push('HERO textos assimetricos'); }
  }
  [...n, ...tx].forEach((r, i) => { if (sob(r, arte)) out.push('HERO texto sobre a arte #' + i); });
  bts.forEach(b => { if (sob(b, arte)) out.push('HERO botao sobre a arte'); });
  tx.forEach(t => bts.forEach(b => { if (t.bottom > b.top + 1 && t.top < b.bottom) out.push('HERO texto sobre botao'); }));
  /* grades: cada linha com cartoes iguais e centrada */
  const lin = s => { const m = {}; [...document.querySelectorAll(s)].filter(e => !e.closest('[hidden]') && !e.hidden).forEach(e => { const r = e.getBoundingClientRect(); (m[Math.round(r.top)] = m[Math.round(r.top)] || []).push(r); }); return Object.values(m); };
  ['#grade .peca', '#disp .pagina', '#cic .peca', '#paginas .pagina', '.vitrine .prod', '.cidades .cidade', '.pilares > *'].forEach(s => lin(s).forEach(l => {
    const w0 = l[0].width, h0 = l[0].height;
    if (l.some(r => Math.abs(r.width - w0) > 1.2 || Math.abs(r.height - h0) > 1.2)) out.push('GRADE ' + s);
    const a = Math.min(...l.map(r => r.left)), b = Math.max(...l.map(r => r.right)); if (Math.abs((a + b) / 2 - eixo) > 1.5) out.push('GRADE fora do eixo ' + s);
  }));
  /* botoes da loja alinhados na mesma linha */
  lin('.vitrine .prod .bt').forEach(() => {});
  const bl = {}; document.querySelectorAll('.vitrine .prod').forEach(p => { const r = p.getBoundingClientRect(), b = p.querySelector('.bt').getBoundingClientRect(); (bl[Math.round(r.top)] = bl[Math.round(r.top)] || []).push(Math.round(b.top)); });
  Object.values(bl).forEach(v => { if (Math.max(...v) - Math.min(...v) > 1) out.push('LOJA botoes desalinhados'); });
  const imgs = [...document.images].filter(i => i.complete && !i.naturalWidth && i.getAttribute('src')); if (imgs.length) out.push('IMG quebrada ' + imgs[0].src.slice(-40));
  return [...new Set(out)];
}
"""
with sync_playwright() as p:
    b = p.chromium.launch(channel='msedge', args=ARG)
    tot = 0
    for w, h, tq in VPS:
        c = b.new_context(viewport={'width': w, 'height': h}, has_touch=bool(tq), is_mobile=bool(tq), device_scale_factor=1)
        g = c.new_page(); er = []
        g.on('pageerror', lambda e: er.append('JS ' + str(e)[:200]))
        g.on('console', lambda m: er.append('CON ' + m.text[:160]) if m.type == 'error' else None)
        g.on('response', lambda r: er.append(f'{r.status} ' + r.url[-50:]) if r.status >= 400 else None)
        g.goto(URL, wait_until='load'); g.wait_for_timeout(1500)
        o = g.evaluate(JS) + er
        print(f'{w}x{h}', 'ok' if not o else '', flush=True)
        for x in o: print('   ', x)
        tot += len(o); c.close()
    print('TOTAL auditoria', tot)
    R = []
    def ok(n, v, x=''):
        R.append(bool(v)); print('OK ' if v else 'FALHOU', n, x, flush=True)
    c = b.new_context(viewport={'width': 1440, 'height': 900}); g = c.new_page()
    g.goto(URL); g.wait_for_timeout(1500)
    vis = lambda: g.evaluate("[...document.querySelectorAll('#grade .peca')].filter(p=>!p.hidden).length")
    tot_p = g.evaluate("DADOS.pecas.length")
    ok('shader ativo', g.evaluate("document.querySelector('#pintura').width") >= 1440)
    g.wait_for_timeout(5000)
    ok('pintura termina (hero pronto)', g.evaluate("document.querySelector('.hero').classList.contains('pronto')"))
    ok('12 de cara', vis() == 12)
    g.evaluate("document.querySelector('.filtros button[data-cat=bichos]').scrollIntoView({block:'center',behavior:'instant'})")
    g.click('.filtros button[data-cat=bichos]'); g.wait_for_timeout(200)
    na = vis(); ok('filtro', 0 < na < tot_p, na)
    g.click('.filtros button[data-cat=todas]'); g.wait_for_timeout(200)
    g.click('#ver-todas'); g.wait_for_timeout(200)
    ok('ver todas', vis() == tot_p, tot_p)
    g.click('#grade .peca:not([hidden]) >> nth=2'); g.wait_for_timeout(800)
    ok('lightbox abre', not g.evaluate("document.querySelector('#lb').hidden"))
    ok('lightbox foto', g.evaluate("(()=>{const i=document.querySelector('#lb-img');return i.complete&&i.naturalWidth>0})()"))
    l0 = g.inner_text('#lb-leg'); g.keyboard.press('ArrowRight'); g.wait_for_timeout(300)
    ok('seta teclado', g.inner_text('#lb-leg') != l0)
    ok('todas as fotos existem', g.evaluate("""async()=>{const D=DADOS,u=[];
      D.pecas.forEach(p=>u.push('assets/img/p/'+p.id+'.webp','assets/img/o/'+p.id+'.webp'));
      D.obras.forEach(o=>u.push('assets/img/obra/'+o.id+'.webp'));
      const r=await Promise.all(u.map(x=>fetch(x,{method:'HEAD'}).then(y=>y.ok)));return r.every(Boolean)}"""))
    leg = g.inner_text('#lb-leg'); g.click('#lb-quero'); g.wait_for_timeout(1300)
    ok('quero uma assim', leg in g.input_value('#f-ref') and g.evaluate("document.querySelector('#lb').hidden"))
    o0 = g.get_attribute('#par-obra', 'src')
    g.click('#obras-sel button >> nth=2'); g.wait_for_timeout(900)
    ok('tela para a pele troca', g.get_attribute('#par-obra', 'src') != o0)
    ok('poema inteiro visivel no PC', g.evaluate("!document.querySelector('#livro-bt').offsetParent"))
    n0 = g.evaluate("[...document.querySelectorAll('#disp .pagina')].filter(p=>!p.hidden).length")
    g.click('#ver-disp'); g.wait_for_timeout(200)
    ok('ver disponiveis', g.evaluate("[...document.querySelectorAll('#disp .pagina')].filter(p=>!p.hidden).length") > n0 or n0 == g.evaluate("DADOS.disp.length"))
    lojas = g.evaluate("[...document.querySelectorAll('.vitrine a')].map(a=>a.href)")
    ok('loja aponta pra Nuvemshop', lojas and all('anymoon.lojavirtualnuvem.com.br' in u for u in lojas), len(lojas))
    g.click('[data-cidade="Belo Horizonte"]'); g.wait_for_timeout(900)
    ok('lista de espera marca cidade', g.evaluate("document.querySelector('.ops[data-nome=cidade] button[aria-pressed=true]').textContent") == 'Belo Horizonte')
    g.fill('#f-nome', ''); g.click('#form button[type=submit]'); g.wait_for_timeout(200)
    ok('erro sem nome', not g.evaluate("document.querySelector('#f-erro').hidden"))
    g.fill('#f-nome', 'Teste'); g.fill('#f-ideia', 'Uma borboleta'); g.click('.ops[data-nome=local] button:nth-child(1)')
    with c.expect_page() as pop: g.click('#form button[type=submit]')
    u = unquote(pop.value.url).replace('+', ' '); pop.value.close()
    ok('whatsapp', '5511983873974' in u and 'borboleta' in u and 'Antebraço' in u and 'Belo Horizonte' in u and leg in u, u[:90])
    c.close()
    c = b.new_context(viewport={'width': 390, 'height': 844}, has_touch=True, is_mobile=True); g = c.new_page()
    g.goto(URL); g.wait_for_timeout(2500)
    ok('video no celular', g.evaluate("(()=>{const v=document.querySelector('.hero video');return !!v&&v.muted&&(v.currentTime>0||!v.paused)})()"))
    g.evaluate("document.querySelector('#livro-bt').scrollIntoView({block:'center',behavior:'instant'})"); g.tap('#livro-bt'); g.wait_for_timeout(400)
    ok('livro abre no celular', not g.evaluate("document.querySelector('#livro').classList.contains('fechado')"))
    g.evaluate("scrollTo(0,0)"); g.wait_for_timeout(300)
    g.tap('.menu-bt'); g.wait_for_timeout(200)
    ok('menu abre', not g.evaluate("document.querySelector('#menu').hidden"))
    g.tap('.menu a[href="#sobre"]'); g.wait_for_timeout(1300)
    ok('menu fecha e rola', g.evaluate("document.querySelector('#menu').hidden && scrollY>500"))
    c.close()
    c = b.new_context(viewport={'width': 390, 'height': 844}, has_touch=True, is_mobile=True); g = c.new_page()
    g.add_init_script("HTMLMediaElement.prototype.play=function(){return Promise.reject(new DOMException('x','NotAllowedError'))}")
    g.goto(URL); g.wait_for_timeout(1800)
    ok('pouca energia cai no shader', g.evaluate("!document.querySelector('.hero video') && document.querySelector('#pintura').width>300"))
    c.close()
    c = b.new_context(viewport={'width': 1280, 'height': 720}, reduced_motion='reduce'); g = c.new_page()
    g.goto(URL); g.wait_for_timeout(1500)
    ok('movimento reduzido mostra quadro final', g.evaluate("document.querySelector('.hero').classList.contains('pronto')"))
    c.close()
    print('FUNCIONAL', sum(R), '/', len(R))
    b.close()
