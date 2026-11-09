# -*- coding: utf-8 -*-
"""Grava o hero do celular (1080x1920, toca uma vez), a imagem final com transparencia, a capa de link e o favicon.
Uso: python tools/gerar_video.py [video] [final] [og] [icone]"""
import base64, io, json, shutil, subprocess, sys, time
from pathlib import Path
from playwright.sync_api import sync_playwright
from PIL import Image
S = Path(__file__).resolve().parent.parent
ff = shutil.which('ffmpeg')
Q = sys.argv[1:] or ['video', 'final', 'og', 'icone']
FPS = 30
b64 = lambda f, m: f'data:{m};base64,' + base64.b64encode((S / f).read_bytes()).decode()
meta = json.loads((S / 'assets/hero/pinceladas.json').read_text())
PAPEL = [241, 233, 221]  # compensa a conversao para yuv (decodifica em 238,231,219)
VW, VH = 1080, 1920

def geo(W, H):  # igual ao site.js (modo em pe)
    s = min(W * .92, H * .43); return (W - s) / 2, H * .5 - s / 2, s

with sync_playwright() as p:
    b = p.chromium.launch(channel='msedge', args=['--use-angle=d3d11', '--ignore-gpu-blocklist', '--enable-gpu'])
    g = b.new_page(viewport={'width': 400, 'height': 400})
    g.set_content('<body style="margin:0"><canvas id=c></canvas></body>')
    g.add_script_tag(content=(S / 'assets/js/pintura.js').read_text(encoding='utf8'))
    g.evaluate("""async(a)=>{window.T=pinturaHero(document.getElementById('c'),{guardar:true,super:1.25});
      const r=await fetch(a.bin);const m=new Image();m.src=a.img;await m.decode();T.carregar(await r.arrayBuffer(),a.meta,m)}""",
               dict(bin=b64('assets/hero/pinceladas.bin', 'application/octet-stream'), meta=meta, img=b64('assets/hero/retrato.webp', 'image/webp')))

    def foto(t, W, H, rect, fundo, fmt='jpeg', q=.95):
        d = g.evaluate(f"(T.quadro({t},{W},{H},1,{json.dumps(rect)},{json.dumps(fundo)}),document.getElementById('c').toDataURL('image/{fmt}',{q}))")
        return base64.b64decode(d.split(',', 1)[1])

    if 'final' in Q:
        L = 1400
        im = Image.open(io.BytesIO(foto(99, L, L, [0, 0, L], None, 'png')))
        im.save(S / 'assets/hero/final.webp', quality=86, method=6)
        print('final', im.size, im.mode, flush=True)
    if 'video' in Q:
        mp4 = S / 'assets/video/hero-pe.mp4'
        dur = g.evaluate('pinturaDuracao') + .5; n = round(dur * FPS)
        x, y, s = geo(VW, VH)
        enc = subprocess.Popen([ff, '-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', str(FPS), '-c:v', 'mjpeg', '-i', '-',
                                '-c:v', 'libx264', '-preset', 'slow', '-crf', '19', '-pix_fmt', 'yuv420p', '-profile:v', 'high',
                                '-color_range', 'tv', '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709',
                                '-vf', 'scale=out_color_matrix=bt709:out_range=tv',
                                '-r', str(FPS), '-movflags', '+faststart', '-an', str(mp4)], stdin=subprocess.PIPE)
        t0 = time.time()
        for i in range(n):
            enc.stdin.write(foto(i / FPS, VW, VH, [x, y, s], PAPEL))
        enc.stdin.close(); enc.wait()
        print(mp4.name, round(mp4.stat().st_size / 1e6, 2), 'MB', round(time.time() - t0), 's', flush=True)
    if 'og' in Q:
        arte = 'data:image/webp;base64,' + base64.b64encode((S / 'assets/hero/final.webp').read_bytes()).decode()
        fn = b64('assets/fonts/cormorant-garamond-500-latin.woff2', 'font/woff2')
        fi = b64('assets/fonts/cormorant-garamond-500i-latin.woff2', 'font/woff2')
        o = b.new_page(viewport={'width': 1200, 'height': 630})
        o.set_content(f'''<style>@font-face{{font-family:F;src:url({fn})}}@font-face{{font-family:F;font-style:italic;src:url({fi})}}
          body{{margin:0;width:1200px;height:630px;background:#eee7db;overflow:hidden;position:relative;color:#2a1d17}}
          img{{position:absolute;left:50%;top:22px;width:586px;height:586px;margin-left:-293px}}
          b{{position:absolute;top:252px;font:500 112px/1 F;font-weight:500}}
          .e{{right:calc(50% + 300px)}} .d{{left:calc(50% + 300px)}}
          i{{position:absolute;top:382px;width:268px;font:italic 500 27px/1.25 F;color:#5c4a3f}}</style>
          <img src="{arte}"><b class=e>Any</b><b class=d>moon</b><i style="right:calc(50% + 302px);text-align:right">Tatuagens inspiradas em pintura e poesia</i><i style="left:calc(50% + 302px)">Butantã, São Paulo</i>''')
        o.wait_for_timeout(600); o.screenshot(path=str(S / 'assets/img/og.jpg'), type='jpeg', quality=88); o.close(); print('og', flush=True)
    if 'icone' in Q:
        fn = b64('assets/fonts/cormorant-garamond-600-latin.woff2', 'font/woff2')
        o = b.new_page(viewport={'width': 512, 'height': 512})
        o.set_content(f'''<style>@font-face{{font-family:F;src:url({fn})}}body{{margin:0;width:512px;height:512px;background:#2a1d17;display:flex;align-items:center;justify-content:center}}
          span{{font:600 400px/1 F;color:#eee7db;transform:translateY(-14px)}}</style><span>A</span>''')
        o.wait_for_timeout(500); png = o.screenshot(type='png'); o.close()
        im = Image.open(io.BytesIO(png)).convert('RGB')
        im.resize((64, 64), Image.LANCZOS).save(S / 'assets/img/favicon.png')
        im.resize((180, 180), Image.LANCZOS).save(S / 'assets/img/apple-touch-icon.png')
        print('icone', flush=True)
    b.close()
