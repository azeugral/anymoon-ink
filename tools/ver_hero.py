# -*- coding: utf-8 -*-
"""Renderiza quadros do hero em tempos fixos para conferir. Uso: python tools/ver_hero.py saida.jpg [lado] [t1,t2,...] [foto]"""
import base64, io, json, sys
from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image
S = Path(__file__).resolve().parent.parent
out = sys.argv[1] if len(sys.argv) > 1 else 'ver.jpg'
L = int(sys.argv[2]) if len(sys.argv) > 2 else 900
TS = [float(x) for x in (sys.argv[3] if len(sys.argv) > 3 else '0.5,1.2,2.0,2.8,3.6,5').split(',')]
FOTO = float(sys.argv[4]) if len(sys.argv) > 4 else 1
b64 = lambda f, m: f'data:{m};base64,' + base64.b64encode((S / f).read_bytes()).decode()
meta = json.loads((S / 'assets/hero/pinceladas.json').read_text())
with sync_playwright() as p:
    b = p.chromium.launch(channel='msedge', args=['--use-angle=d3d11', '--ignore-gpu-blocklist', '--enable-gpu'])
    g = b.new_page(viewport={'width': L, 'height': L})
    g.on('console', lambda m: print('CON', m.text))
    g.set_content('<body style="margin:0;background:#ece4d6"><canvas id=c></canvas></body>')
    g.add_script_tag(content=(S / 'assets/js/pintura.js').read_text(encoding='utf8'))
    g.evaluate("""async(a)=>{window.T=pinturaHero(document.getElementById('c'),{guardar:true,foto:a.foto});
      const r=await fetch(a.bin);const m=new Image();m.src=a.img;await m.decode();T.carregar(await r.arrayBuffer(),a.meta,m)}""",
               dict(bin=b64('assets/hero/pinceladas.bin', 'application/octet-stream'), meta=meta, img=b64('assets/hero/retrato.webp', 'image/webp'), foto=FOTO))
    ims = []
    for t in TS:
        d = g.evaluate(f"(T.quadro({t},{L},{L},1,[0,0,{L}],[236,228,214]),document.getElementById('c').toDataURL('image/jpeg',.92))")
        ims.append(Image.open(io.BytesIO(base64.b64decode(d.split(',', 1)[1]))))
    W = sum(i.width for i in ims); o = Image.new('RGB', (W, L))
    x = 0
    for i in ims: o.paste(i, (x, 0)); x += i.width
    o.save(out, quality=90)
    b.close()
print('ok', out)
