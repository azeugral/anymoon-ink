# -*- coding: utf-8 -*-
"""Prepara todas as imagens do site a partir de _ref e gera assets/js/dados.js.
Uso: python tools/fotos.py"""
import json
from pathlib import Path
from PIL import Image, ImageFilter, ImageOps

S = Path(__file__).resolve().parent.parent
R = S.parent / '_ref'
A = S / 'assets/img'

def salva(im, dest, lado=None, q=82):
    dest.parent.mkdir(parents=True, exist_ok=True)
    if lado and max(im.size) > lado:
        im = im.copy(); im.thumbnail((lado, lado), Image.LANCZOS)
    im.save(dest, quality=q, method=6)

def corta(im, cx=.5, cy=.5, h=None, prop=.8):
    """recorte prop (largura/altura) centrado em cx, cy; h = fracao da altura"""
    W, H = im.size
    if h is None:
        ch = min(H, W / prop); cw = ch * prop
    else:
        ch = h * H; cw = ch * prop
        if cw > W: cw = W; ch = cw / prop
    x = min(max(0, cx * W - cw / 2), W - cw); y = min(max(0, cy * H - ch / 2), H - ch)
    return im.crop((round(x), round(y), round(x + cw), round(y + ch)))

def nitida(im):
    return im.filter(ImageFilter.UnsharpMask(radius=1.2, percent=40, threshold=2))

# ---------- portfolio ----------
PECAS = [  # id, foto, categoria, titulo, cy
    ('ofelia', '077_0', 'obras', 'Ofélia, de John Everett Millais', .5),
    ('lirios', '083_0', 'obras', 'Lírios, de Van Gogh', .45),
    ('girassois', '044_0', 'obras', 'Girassóis, de Van Gogh', .42),
    ('amendoeira', '029_0', 'obras', 'Amendoeira em flor, de Van Gogh', .45),
    ('noite', '055_1', 'obras', 'Uma pincelada da Noite Estrelada', .5),
    ('noite-girassois', '079_0', 'obras', 'A Noite Estrelada e Os Girassóis', .5),
    ('olhares', '090_1', 'obras', 'Olhares que atravessam séculos', .5),
    ('dali', '113_0', 'obras', 'Salvador Dalí', .5),
    ('magritte', '130_1', 'obras', 'Releitura de René Magritte', .5),
    ('vader', '072_1', 'historias', 'Darth Vader dentro da Noite Estrelada', .5),
    ('totoro', '084_0', 'historias', 'Totoro Gogh', .5),
    ('astarion', '022_0', 'historias', 'The Fallen Angel com Astarion', .5),
    ('tartarugas', '057_0', 'historias', 'Tartarugas Ninja, os mestres da arte', .5),
    ('bem-te-vi', '010_2', 'jardim', 'Jardim da memória: o bem-te-vi', .5),
    ('lar', '019_0', 'jardim', 'Jardim da memória: o abraço de um lar', .5),
    ('viajante', '070_1', 'jardim', 'O pássaro viajante', .5),
    ('borboleta', '016_2', 'bichos', 'A beleza das transformações', .5),
    ('little-women', '009_2', 'historias', 'Little Women', .5),
    ('matt', '004_1', 'bichos', 'Em homenagem ao Matt', .5),
    ('nina', '026_1', 'bichos', 'Nina', .5),
    ('gatinho', '063_1', 'bichos', 'Gatinho em homenagem', .5),
    ('chiquinho', '101_1', 'bichos', 'Gatinho inspirado no Chiquinho', .5),
    ('sapo', '109_1', 'bichos', 'O sapo de suéter', .5),
    ('cervo', '119_0', 'bichos', 'Cervo', .5),
    ('cisne', '036_0', 'bichos', 'Cisne sob o lago', .5),
    ('botanica', '048_1', 'flores', 'Botânica viva na pele', .5),
    ('jardim-braco', '066_1', 'flores', 'Um jardim no braço', .5),
    ('fechamento', '112_0', 'flores', 'Fechamento de flores', .5),
    ('lirio', '117_0', 'flores', 'Lírio laranja', .5),
    ('girassol', '124_1', 'flores', 'Girassol', .5),
    ('morango', '014_0', 'flores', 'Moranguinho', .5),
    ('pokemon', '054_2', 'historias', 'Pokémon, 30 anos na pele', .5),
    ('relicario', '061_1', 'historias', 'Relicário, A Noiva Cadáver', .5),
    ('ursinho', '065_0', 'historias', 'Ursinho emo', .5),
    ('ghibli', '104_1', 'historias', 'Bracelete do Studio Ghibli', .5),
    ('branca', '106_1', 'historias', 'Branca de Neve', .5),
    ('monstros', '027_4', 'historias', 'Cobertura com Onde Vivem os Monstros', .5),
    ('sereia', '086_1', 'historias', 'Sereia', .5),
]
pecas = []
for pid, f, cat, tit, cy in PECAS:
    im = Image.open(R / f'ig/fotos/{f}.jpg').convert('RGB')
    c = corta(im, .5, cy)
    salva(nitida(c.resize((720, 900), Image.LANCZOS)), A / f'p/{pid}.webp', q=80)
    salva(c, A / f'o/{pid}.webp', 1500, q=84)
    pecas.append({'id': pid, 'cat': cat, 't': tit})
print('portfolio', len(pecas))

# ---------- da tela para a pele ----------
OBRAS = [  # id da obra, arquivo, nome, artista e ano, peca
    ('noite', 'noite', 'A Noite Estrelada', 'Vincent van Gogh, 1889', 'noite'),
    ('ofelia', 'ofelia', 'Ofélia', 'John Everett Millais, 1851–52', 'ofelia'),
    ('lirios', 'lirios', 'Lírios', 'Vincent van Gogh, 1889', 'lirios'),
    ('amendoeira', 'amendoeira', 'Amendoeira em flor', 'Vincent van Gogh, 1890', 'amendoeira'),
    ('girassois', 'girassois', 'Girassóis', 'Vincent van Gogh, 1888', 'girassois'),
]
obras = []
for oid, arq, nome, autor, peca in OBRAS:
    im = Image.open(R / f'obras/{arq}.jpg').convert('RGB')
    salva(im, A / f'obra/{oid}.webp', 1100, q=84)
    obras.append({'id': oid, 'nome': nome, 'autor': autor, 'peca': peca, 'w': min(im.width, 1100) if im.width >= im.height else round(1100 * im.width / im.height), 'h': round(min(im.width, 1100) * im.height / im.width) if im.width >= im.height else 1100})
print('obras', len(obras))

# ---------- disponiveis e jardim da memoria (paginas dela, 9:16) ----------
DISP = [  # arquivo, titulo
    ('13', 'A raposa viajante'), ('34', 'Gatozila'), ('23', 'Eu levo meu lar comigo'), ('24', 'Eu sou meu próprio lar'),
    ('32', 'O gato pintor'), ('17', 'Copo-de-leite'), ('36', 'Van Gogh na janela'), ('35', 'Van Gogh em azul'),
    ('21', 'Folha de obras I'), ('22', 'Folha de obras II'), ('31', 'Folha de obras III'), ('33', 'Frutas'),
    ('07', 'Folha Van Gogh'), ('06', 'Folha clássica'), ('04', 'Folha de natureza'), ('18', 'Fragmentos de obras'),
]
disp = []
for f, t in DISP:
    im = Image.open(R / f'hl/disponiveis/{f}.jpg').convert('RGB')
    im = corta(im, .5, .5, prop=9 / 16)
    salva(im.resize((540, 960), Image.LANCZOS), A / f'd/{f}.webp', q=82)
    salva(im, A / f'dg/{f}.webp', 1472, q=84)
    disp.append({'id': f, 't': t})
JARDIM = [('08', 'Memórias que aquecem'), ('09', 'Como quem volta pra casa'), ('10', 'Crescer é aprender a olhar de novo'), ('11', 'No gesto de lembrar')]
jardim = []
for f, t in JARDIM:
    im = Image.open(R / f'hl/disponiveis/{f}.jpg').convert('RGB')
    im = corta(im, .5, .5, prop=9 / 16)
    salva(im.resize((540, 960), Image.LANCZOS), A / f'j/{f}.webp', q=84)
    salva(im, A / f'jg/{f}.webp', 1472, q=86)
    jardim.append({'id': f, 't': t})
print('disponiveis', len(disp), 'jardim', len(jardim))

# ---------- cicatrizadas ----------
CIC = [  # arquivo, cx, cy, h, legenda
    ('07', .5, .5, .44, 'Noite Estrelada, 2 meses'),
    ('14', .5, .55, .42, 'O Beijo, de Klimt'),
    ('16', .5, .54, .4, 'Cicatrizada há 1 ano e 3 meses'),
    ('22', .5, .45, .44, 'TARDIS na Noite Estrelada'),
    ('33', .5, .48, .36, 'Releitura de Magritte'),
    ('38', .5, .5, .52, 'Cicatrizada há 1 ano'),
    ('41', .5, .55, .5, 'A Noite e Os Girassóis'),
    ('44', .5, .45, .38, 'Noite Estrelada, 2 anos'),
]
cic = []
for f, cx, cy, h, t in CIC:
    im = Image.open(R / f'hl/cicatrizadas/{f}.jpg').convert('RGB')
    c = corta(im, cx, cy, h)
    salva(nitida(c.resize((640, 800), Image.LANCZOS)), A / f'c/{f}.webp', q=82)
    cic.append({'id': f, 't': t})
print('cicatrizadas', len(cic))

# ---------- loja (Nuvemshop) ----------
L = json.loads((R / 'loja/lista.json').read_text(encoding='utf8'))
PRECO = {'estou-indo-original-etd95': 150, 'sou-casa-original-colecao-carrego-meu-lar-1jfuy': 350, 'casa-original-colecao-carrego-meu-lar-7n6ng': 250,
         'bem-te-vi-original-colecao-jardim-da-memoria-ahscr': 400, 'van-gogh-em-miniatura': 200}
NOME = {'estou-indo-original-etd95': ('Estou indo', 'Original em lápis de cor'), 'sou-casa-original-colecao-carrego-meu-lar-1jfuy': ('Sou casa', 'Coleção Carrego meu lar'),
        'casa-original-colecao-carrego-meu-lar-7n6ng': ('Casa', 'Coleção Carrego meu lar'), 'bem-te-vi-original-colecao-jardim-da-memoria-ahscr': ('Bem-te-vi', 'Coleção Jardim da memória'),
        'van-gogh-em-miniatura': ('Van Gogh em miniatura', 'Pintura com cavalete')}
ORDEM = ['bem-te-vi-original-colecao-jardim-da-memoria-ahscr', 'sou-casa-original-colecao-carrego-meu-lar-1jfuy', 'van-gogh-em-miniatura', 'casa-original-colecao-carrego-meu-lar-7n6ng', 'estou-indo-original-etd95']
loja = []
for slug in ORDEM:
    r = next(x for x in L if slug in x['url'])
    i = L.index(r)
    for k in (0, 1):
        im = Image.open(R / f'loja/p{i}_{k}.webp').convert('RGB')
        im = corta(im, .5, .5, prop=4 / 5)
        salva(im.resize((640, 800), Image.LANCZOS), A / f'l/{slug[:12]}-{k}.webp', q=82)
    loja.append({'id': slug[:12], 'nome': NOME[slug][0], 'linha': NOME[slug][1], 'preco': PRECO[slug], 'url': r['url']})
print('loja', len(loja))

# ---------- retratos ----------
im = Image.open(R / 'ig/fotos/082_0.jpg').convert('RGB')
salva(corta(im, .5, .45), A / 'sobre.webp', 1100, q=84)
im = Image.open(R / 'ig/fotos/040_0.jpg').convert('RGB')
salva(corta(im, .5, .42), A / 'retrato-2.webp', 1100, q=84)
im = Image.open(R / 'ig/fotos/060_0.jpg').convert('RGB')
salva(corta(im, .5, .5), A / 'caderno.webp', 1100, q=84)

(S / 'assets/js/dados.js').write_text('window.DADOS=' + json.dumps({'pecas': pecas, 'obras': obras, 'disp': disp, 'jardim': jardim, 'cic': cic, 'loja': loja}, ensure_ascii=False) + ';\n', encoding='utf8')
print('dados.js ok')
