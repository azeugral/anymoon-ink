# -*- coding: utf-8 -*-
"""Capturas para conferir: hero em varios tamanhos + pagina inteira. Uso: python tools/telas.py [url] [pasta]"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright
URL = next((a for a in sys.argv[1:] if a.startswith('http')), 'http://localhost:8920/')
OUT = Path(next((a for a in sys.argv[1:] if not a.startswith('http')), '../_ref/telas')); OUT.mkdir(parents=True, exist_ok=True)
VPS = [(1440, 900, 0), (1280, 720, 0), (1920, 1080, 0), (390, 844, 1), (360, 640, 1), (320, 568, 1), (768, 1024, 1), (844, 390, 1)]
with sync_playwright() as p:
    b = p.chromium.launch(channel='msedge', args=['--use-angle=d3d11', '--ignore-gpu-blocklist', '--enable-gpu', '--autoplay-policy=no-user-gesture-required'])
    for w, h, m in VPS:
        c = b.new_context(viewport={'width': w, 'height': h}, is_mobile=bool(m), has_touch=bool(m), device_scale_factor=1)
        g = c.new_page(); g.on('pageerror', lambda e: print('JS', e)); g.on('console', lambda x: print('CON', x.text) if x.type == 'error' else None)
        g.goto(URL); g.wait_for_timeout(6500)
        g.screenshot(path=str(OUT / f'hero-{w}x{h}.png'))
        if (w, h) in ((1440, 900), (390, 844)):
            g.evaluate("document.querySelectorAll('.revela').forEach(e=>e.classList.add('visto'))")
            g.evaluate("async()=>{for(let y=0;y<document.body.scrollHeight;y+=600){scrollTo(0,y);await new Promise(r=>setTimeout(r,280))}scrollTo(0,0)}")
            g.wait_for_timeout(1200)
            g.screenshot(path=str(OUT / f'pagina-{w}.png'), full_page=True)
        c.close()
    b.close()
print('ok', OUT)
