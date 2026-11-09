# -*- coding: utf-8 -*-
"""Gera as pinceladas do hero a partir do retrato da Any.
Cada pincelada e uma curva (Bezier quadratica) que segue o fluxo do retrato,
como nas releituras de Van Gogh dela. Camadas da mais grossa a mais fina.
Saida: assets/hero/pinceladas.bin (Uint16 x 10 por pincelada) + pinceladas.json + retrato.webp
Uso: python tools/pinceladas.py"""
import json, math
from pathlib import Path
import numpy as np, cv2
from PIL import Image

S = Path(__file__).resolve().parent.parent
REF = S.parent / '_ref'
rng = np.random.default_rng(7)

# --- retrato: mistura do Real-ESRGAN (bordas) com Lanczos (textura da pele) ---
orig = Image.open(REF / 'foto-enviada.jpg').convert('RGB')
x4 = Image.open(REF / 'retrato/any-x4.png').convert('RGB').resize((1600, 1600), Image.LANCZOS)
lz = orig.resize((1600, 1600), Image.LANCZOS)
mix = Image.blend(x4, lz, .5)
mix.save(S / 'assets/hero/retrato.webp', quality=90, method=6)

N = 1024
img = np.asarray(orig.resize((N, N), Image.LANCZOS)).astype(np.float32) / 255.
lab = cv2.cvtColor(img, cv2.COLOR_RGB2LAB)
lum = lab[..., 0] / 100.

def ruido(sz, esc, sem):
    r = np.random.default_rng(sem).random((sz // esc + 3, sz // esc + 3)).astype(np.float32)
    return cv2.resize(r, (sz + esc * 2, sz + esc * 2), interpolation=cv2.INTER_CUBIC)[esc:esc + sz, esc:esc + sz]

# --- mascara do quadro: oval com borda de pincel ---
yy, xx = np.mgrid[0:N, 0:N].astype(np.float32) / N
oval = np.sqrt(((xx - .5) / .445) ** 2 + ((yy - .49) / .455) ** 2)
borda = (ruido(N, 48, 1) - .5) * .16 + (ruido(N, 12, 2) - .5) * .06
MASK = (oval + borda) < 1.0
_n, _lab, _st, _ = cv2.connectedComponentsWithStats(MASK.astype(np.uint8))
MASK = _lab == (1 + int(np.argmax(_st[1:, cv2.CC_STAT_AREA])))   # so a mancha principal, sem ilhas soltas

# --- rosto e mao: onde a tinta fina precisa chegar ---
def elipse(cx, cy, rx, ry):
    return np.clip(1.25 - np.sqrt(((xx - cx) / rx) ** 2 + ((yy - cy) / ry) ** 2), 0, 1)
ROSTO = np.clip(elipse(.43, .30, .17, .22) * 1.6 + elipse(.53, .45, .12, .2) * .9, 0, 1)

# --- campo de direcao: tensor de estrutura + redemoinho suave onde a imagem e lisa ---
def tensor(sig):
    gx = cv2.Sobel(lum, cv2.CV_32F, 1, 0, ksize=3); gy = cv2.Sobel(lum, cv2.CV_32F, 0, 1, ksize=3)
    jxx = cv2.GaussianBlur(gx * gx, (0, 0), sig); jyy = cv2.GaussianBlur(gy * gy, (0, 0), sig); jxy = cv2.GaussianBlur(gx * gy, (0, 0), sig)
    raiz = np.sqrt((jxx - jyy) ** 2 + 4 * jxy ** 2)
    coer = (raiz / (jxx + jyy + 1e-6)) ** 2 * np.clip((jxx + jyy) * 60, 0, 1)
    return np.cos(2 * (.5 * np.arctan2(2 * jxy, jxx - jyy) + np.pi / 2)), np.sin(2 * (.5 * np.arctan2(2 * jxy, jxx - jyy) + np.pi / 2)), coer

_pot = ruido(N, 220, 5) + .4 * ruido(N, 110, 6)
_px = cv2.Sobel(_pot, cv2.CV_32F, 1, 0, ksize=5); _py = cv2.Sobel(_pot, cv2.CV_32F, 0, 1, ksize=5)
_sw = np.arctan2(_py, _px) + np.pi / 2

def campo(sig):
    """mistura das escalas pesada pela coerencia: segue o cabelo; onde nada tem direcao, um giro suave"""
    vx = np.zeros((N, N), np.float32); vy = np.zeros_like(vx); pes = np.zeros_like(vx)
    for k in (1, 2.2, 4.5):
        cx, sx, co = tensor(sig * k)
        vx += cx * co; vy += sx * co; pes += co
    fraco = np.clip(1 - pes * 1.4, 0, 1) * .35
    vx += np.cos(2 * _sw) * fraco; vy += np.sin(2 * _sw) * fraco
    return .5 * np.arctan2(vy, vx)

def amostra(a, x, y):
    return a[min(N - 1, max(0, int(y))), min(N - 1, max(0, int(x)))]

def traca(ang, x, y, comp, passo):
    """segue o campo para frente e para tras; devolve inicio, meio e fim"""
    pts = [(x, y)]
    for sgn in (1, -1):
        cx, cy = x, y; dx0 = dy0 = None
        for _ in range(int(comp / 2 / passo)):
            a = amostra(ang, cx, cy); dx, dy = math.cos(a), math.sin(a)
            if dx0 is None:
                dx, dy = dx * sgn, dy * sgn
            elif dx * dx0 + dy * dy0 < 0:
                dx, dy = -dx, -dy
            cx += dx * passo; cy += dy * passo; dx0, dy0 = dx, dy
            if not (0 <= cx < N and 0 <= cy < N) or not amostra(MASK, cx, cy): break
            if sgn > 0: pts.append((cx, cy))
            else: pts.insert(0, (cx, cy))
    return pts[0], pts[len(pts) // 2], pts[-1]

CAMADAS = [  # raio, espacamento, limiar de detalhe, peso do rosto
    (34, .62, -1, 0), (21, .78, .006, 0), (12.5, .95, .014, .25), (7, .9, .018, .55), (4, .85, .030, .8), (2.4, .8, .042, 1.0)]
ests = []
prev = cv2.GaussianBlur(img, (0, 0), 40)
for li, (r, esp, lim, pr) in enumerate(CAMADAS):
    ang = campo(max(2.5, r * .45))
    alvo = cv2.GaussianBlur(img, (0, 0), max(.8, r * .35))
    dif = np.linalg.norm(cv2.GaussianBlur(alvo - prev, (0, 0), r * .6), axis=2)
    passo = r * esp
    gy, gx = np.mgrid[passo / 2:N:passo, passo / 2:N:passo]
    gx = gx + rng.uniform(-.5, .5, gx.shape) * passo; gy = gy + rng.uniform(-.5, .5, gy.shape) * passo
    n0 = len(ests)
    for x, y in zip(gx.ravel(), gy.ravel()):
        if not (0 <= x < N and 0 <= y < N) or not amostra(MASK, x, y): continue
        if lim > 0 and amostra(dif, x, y) < lim * (1 - pr * amostra(ROSTO, x, y)): continue
        comp = r * rng.uniform(2.2, 4.0)
        p0, pm, p2 = traca(ang, x, y, comp, max(1., r / 2.5))
        c = alvo[int(pm[1]), int(pm[0])].copy()
        c = np.clip(c * rng.uniform(.95, 1.05) + rng.normal(0, .012, 3), 0, 1)
        p1 = (2 * pm[0] - (p0[0] + p2[0]) / 2, 2 * pm[1] - (p0[1] + p2[1]) / 2)
        ests.append((p0, p1, p2, r * rng.uniform(.82, 1.0), c, li, x, y))
    prev = alvo
    print('camada', li, 'raio', r, 'pinceladas', len(ests) - n0, flush=True)

# --- tempo: cada camada entra varrendo da base para o topo, com acaso ---
DUR = [.95, .85, .8, .75, .7, .6]; INI = [0, .55, 1.15, 1.7, 2.2, 2.6]
dados = np.zeros((len(ests), 10), np.uint16)
q = lambda v, lo, hi: np.uint16(np.clip((v - lo) / (hi - lo), 0, 1) * 65535)
for i, (p0, p1, p2, w, c, li, x, y) in enumerate(ests):
    var = (1 - y / N) * .55 + abs(x / N - .5) * .3 + rng.uniform(0, .45)
    t0 = INI[li] + var / 1.3 * DUR[li]
    dados[i] = [q(p0[0], -64, N + 64), q(p0[1], -64, N + 64), q(p1[0], -64, N + 64), q(p1[1], -64, N + 64), q(p2[0], -64, N + 64), q(p2[1], -64, N + 64),
                q(w, 0, 48), q(t0, 0, 4), int(c[0] * 255) | (int(c[1] * 255) << 8), int(c[2] * 255) | (li << 8)]
ordem = np.argsort(dados[:, 9] >> 8, kind='stable')  # camadas grossas por baixo
dados = dados[ordem]
(S / 'assets/hero/pinceladas.bin').write_bytes(dados.tobytes())
json.dump({'n': len(dados), 'N': N, 'pad': 64, 'wmax': 48, 'tmax': 4, 'fim': 3.45}, open(S / 'assets/hero/pinceladas.json', 'w'))
print('total', len(dados), round(len(dados) * 20 / 1e3), 'KB')
