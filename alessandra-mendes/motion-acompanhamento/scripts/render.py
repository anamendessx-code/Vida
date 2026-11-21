"""Motion 'Acompanhamento real' · Alê da Pele (1080x1920, 30 fps).

usage: python3 render.py <chunk> <n_chunks>   -> ../out/chunk_XX.mp4 (sem áudio)
       python3 render.py still <t> [t ...]     -> ../out/still_<t>.png
Tempos sincronizados com ../audio/take2.mp3 (narração começa em VO segundos).
"""
import os, sys, math, functools, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, '..', 'out')
W, H, FPS = 1080, 1920, 30
VO = 0.4
DUR = 57.5

PORC = (250, 246, 242); INK = (43, 31, 26); INK2 = (110, 90, 80); CLAY = (185, 112, 90)
CLAYD = (151, 82, 62); BLUSH = (243, 220, 210); PEACH = (247, 201, 178); CHAMP = (234, 211, 174)
WA = (37, 211, 102); WADARK = (7, 94, 84); WHITE = (255, 255, 255); SAGE = (127, 156, 130)

FD = '/usr/share/fonts/opentype/inter/InterDisplay-'
FM = '/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-'

def clamp(x, a=0.0, b=1.0): return a if x < a else b if x > b else x
def eo(p): p = clamp(p); return 1 - (1 - p) ** 3
def eio(p): p = clamp(p); return 4 * p ** 3 if p < .5 else 1 - (-2 * p + 2) ** 3 / 2
def eback(p): p = clamp(p); c1 = 1.70158; c3 = c1 + 1; return 1 + c3 * (p - 1) ** 3 + c1 * (p - 1) ** 2
def lerp(a, b, p): return a + (b - a) * p
def T(a): return a + VO   # tempo da narração -> tempo do vídeo

@functools.lru_cache(None)
def font(weight, size, mono=False):
    return ImageFont.truetype((FM if mono else FD) + weight + ('.ttf' if mono else '.otf'), int(size))

@functools.lru_cache(4096)
def text_img(txt, weight='Black', size=100, color=INK, mono=False, tracking=0):
    f = font(weight, size, mono)
    asc, desc = f.getmetrics()
    wid = sum(f.getlength(c) for c in txt) + tracking * max(0, len(txt) - 1) if tracking else f.getlength(txt)
    pad = 8
    im = Image.new('RGBA', (int(math.ceil(wid)) + 2 * pad, asc + desc + 2 * pad), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if tracking:
        x = pad
        for c in txt:
            d.text((x, pad), c, font=f, fill=color + (255,)); x += f.getlength(c) + tracking
    else:
        d.text((pad, pad), txt, font=f, fill=color + (255,))
    return im

def with_alpha(im, a):
    if a >= 0.999: return im
    im = im.copy(); al = im.getchannel('A').point(lambda v: int(v * a)); im.putalpha(al); return im

def put(c, im, x, y, a=1.0, anchor='c', scale=1.0):
    if a <= 0.004: return
    if abs(scale - 1) > 0.003:
        im = im.resize((max(1, int(im.width * scale)), max(1, int(im.height * scale))), Image.LANCZOS)
    im = with_alpha(im, a)
    if anchor == 'c': x0, y0 = x - im.width // 2, y - im.height // 2
    elif anchor == 'l': x0, y0 = x, y - im.height // 2
    elif anchor == 'r': x0, y0 = x - im.width, y - im.height // 2
    else: x0, y0 = x, y
    c.alpha_composite(im, (int(x0), int(y0)))

def window(t, t0, t1, din=0.35, dout=0.3):
    return clamp((t - t0) / din) * (1 - clamp((t - (t1 - dout)) / dout))

def rise(c, im, x, y, t, t0, t1, anchor='c', dy=60, dur=0.55):
    p = eo((t - t0) / dur); a = window(t, t0, t1, dur * .7)
    put(c, im, x, y + (1 - p) * dy, a, anchor)

def pop(c, im, x, y, t, t0, t1, s0=1.25, dur=0.45):
    p = clamp((t - t0) / dur); a = window(t, t0, t1, dur * .6)
    put(c, im, x, y, a, 'c', lerp(s0, 1.0, eback(p)) if p < 1 else 1.0)

def rrect(w, h, r, fill, outline=None, ow=0):
    im = Image.new('RGBA', (int(w), int(h)), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle((0, 0, w - 1, h - 1), r, fill=fill, outline=outline, width=ow)
    return im

@functools.lru_cache(256)
def pill(txt, size=34, fill=CLAY, color=WHITE, weight='Bold', padx=28, pady=14, mono=False, outline=None):
    t = text_img(txt, weight, size, color, mono)
    p = rrect(t.width + padx * 2, t.height + pady * 2, (t.height + pady * 2) // 2, fill + (255,) if len(fill) == 3 else fill, outline, 3 if outline else 0)
    p.alpha_composite(t, (padx, pady)); return p

def shadow_card(w, h, r=46, fill=WHITE, blur=28, op=70):
    return _shadow_card(w, h, r, fill, blur, op).copy()

@functools.lru_cache(64)
def _shadow_card(w, h, r=46, fill=WHITE, blur=28, op=70):
    pad = blur * 2
    im = Image.new('RGBA', (w + pad * 2, h + pad * 2), (0, 0, 0, 0))
    sh = Image.new('RGBA', im.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).rounded_rectangle((pad, pad + 18, pad + w, pad + h + 18), r, fill=(110, 62, 42, op))
    sh = sh.filter(ImageFilter.GaussianBlur(blur))
    im.alpha_composite(sh)
    ImageDraw.Draw(im).rounded_rectangle((pad, pad, pad + w, pad + h), r, fill=fill + (255,) if len(fill) == 3 else fill)
    return im

# --------------------------------------------------------------- fundo
def background(t):
    sw, sh = 135, 240
    yy, xx = np.mgrid[0:sh, 0:sw].astype(np.float32)
    img = np.ones((sh, sw, 3), np.float32) * np.array(PORC, np.float32)
    blobs = [(PEACH, .22 + .10 * math.sin(t * .23), .18 + .06 * math.cos(t * .19), .55),
             (CHAMP, .82 + .08 * math.cos(t * .21), .30 + .08 * math.sin(t * .17), .50),
             (BLUSH, .40 + .12 * math.sin(t * .15 + 1), .78 + .06 * math.cos(t * .2), .55)]
    for col, cx, cy, s in blobs:
        g = np.exp(-(((xx / sw - cx) ** 2) / (2 * (s * .42) ** 2) + ((yy / sh - cy) ** 2) / (2 * (s * .32) ** 2)))[..., None] * .85
        img = img * (1 - g) + np.array(col, np.float32) * g
    im = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).resize((W, H), Image.BILINEAR).convert('RGBA')
    return im

# --------------------------------------------------------------- texto em palavras
def words_layout(text, size, weight, max_w, lh=1.06):
    f = font(weight, size); sp = f.getlength(' ')
    lines, cur, cw = [], [], 0
    for wd in text.split(' '):
        ww = f.getlength(wd)
        if cur and cw + sp + ww > max_w:
            lines.append((cur, cw)); cur, cw = [wd], ww
        else:
            cw = cw + (sp if cur else 0) + ww; cur.append(wd)
    if cur: lines.append((cur, cw))
    return lines, sp, size * lh

def words(c, text, x, y, t, t0, t1, size=96, weight='Black', color=INK, hi=(), hicolor=CLAY, max_w=920, align='c', stagger=0.07, dy=50):
    lines, sp, lh = words_layout(text, size, weight, max_w)
    tot = len(lines) * lh; k = 0
    for li, (ws, lw) in enumerate(lines):
        yy = y - tot / 2 + li * lh + lh / 2
        xx = x - lw / 2 if align == 'c' else x
        for wd in ws:
            col = hicolor if wd.strip('.,?!:…').lower() in hi else color
            im = text_img(wd, weight, size, col)
            p = eo((t - t0 - k * stagger) / 0.5); a = window(t, t0 + k * stagger, t1, 0.35)
            put(c, im, xx - 8, yy + (1 - p) * dy, a, 'l')
            xx += font(weight, size).getlength(wd) + sp; k += 1

def label(c, txt, x, y, t, t0, t1, color=CLAYD, size=30):
    rise(c, text_img(txt.upper(), 'Bold', size, color, True, 4), x, y, t, t0, t1, dy=24)

# --------------------------------------------------------------- malha facial
def landmarks(cx, cy, s):
    P = []
    for i in range(17):
        a = math.radians(190 + i * 10); P.append((cx + 96 * s * math.cos(a), cy - 8 * s - 128 * s * math.sin(a)))
    for d in (-1, 1):
        for i in range(5):
            u = i / 4; P.append((cx + d * (22 + 58 * u) * s, cy - 58 * s - math.sin(u * math.pi) * 12 * s + u * 6 * s))
    for i in range(4): P.append((cx, cy - 34 * s + i * 16 * s))
    for i in range(5): P.append((cx + (i - 2) * 10 * s, cy + 34 * s - abs(i - 2) * 3 * s))
    for d in (-1, 1):
        ex, ey = cx + d * 46 * s, cy - 20 * s
        for u, v in [(-1, 0), (-.45, -.55), (.45, -.55), (1, 0), (.45, .45), (-.45, .45)]: P.append((ex + u * 17 * s * d, ey + v * 12 * s))
    my = cy + 72 * s
    for u, v in [(-1, 0), (-.6, -.45), (-.2, -.6), (0, -.5), (.2, -.6), (.6, -.45), (1, 0), (.6, .6), (.2, .8), (0, .8), (-.2, .8), (-.6, .6)]:
        P.append((cx + u * 30 * s, my + v * 16 * s))
    return P
GROUPS = [(0, 17, 0), (17, 22, 0), (22, 27, 0), (27, 31, 0), (31, 36, 0), (36, 42, 1), (42, 48, 1), (48, 60, 1)]
EXTRA = [(0, 36), (16, 45), (2, 48), (14, 54), (8, 57), (31, 48), (35, 54), (27, 39), (27, 42), (17, 36), (26, 45), (21, 27), (22, 27), (3, 31), (13, 35)]

def mesh(c, cx, cy, s, prog, color=WHITE, a=1.0):
    if a <= 0: return
    P = landmarks(cx, cy, s)
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    E = []
    for a0, b0, cl in GROUPS:
        for i in range(a0, b0 - 1): E.append((i, i + 1))
        if cl: E.append((b0 - 1, a0))
    E += EXTRA
    lp = clamp((prog - .25) / .6)
    for k, (i, j) in enumerate(E):
        q = clamp(lp * len(E) - k * .7)
        if q <= 0: continue
        x2 = P[i][0] + (P[j][0] - P[i][0]) * q; y2 = P[i][1] + (P[j][1] - P[i][1]) * q
        d.line((P[i][0], P[i][1], x2, y2), fill=color + (int(170 * a),), width=2)
    n = int(len(P) * clamp(prog * 1.6))
    for i in range(n):
        x, y = P[i]; d.ellipse((x - 4, y - 4, x + 4, y + 4), fill=color + (int(255 * a),))
    c.alpha_composite(lay)

# --------------------------------------------------------------- cenas
def topbar(c, t):
    a = clamp(t / 0.6) * (1 - clamp((t - (T(50.86) - .3)) / .4))
    if a <= 0: return
    put(c, pill('AM', 28, INK, PORC, 'Bold', 18, 12), 90, 150, a, 'l')
    put(c, text_img('ALÊ DA PELE', 'Bold', 26, INK2, True, 5), 190, 150, a, 'l')
    # barra de progresso
    p = clamp(t / T(50.86))
    bar = Image.new('RGBA', (W - 180, 6), (43, 31, 26, 40)); ImageDraw.Draw(bar).rectangle((0, 0, int((W - 180) * p), 6), fill=CLAY + (255,))
    put(c, bar, 90, 210, a, 'tl')

def s1(c, t):  # cansada de gastar
    t0, t1 = 0.0, T(4.70)
    if not (t0 <= t <= t1): return
    label(c, 'Você também?', W // 2, 620, t, T(0.0), t1)
    words(c, 'Cansada de gastar dinheiro com a sua pele', W // 2, 840, t, T(0.05), t1, 104, hi=('dinheiro',))
    words(c, 'e nada dar resultado?', W // 2, 1180, t, T(2.9), t1, 92, 'ExtraBoldItalic', CLAY)
    # contador de gastos
    v = int(lerp(150, 8740, eio((t - T(0.4)) / 3.6)))
    s = 'R$ ' + f'{v:,}'.replace(',', '.')
    card = pill(s, 58, WHITE, (192, 69, 58), 'Bold', 36, 20, outline=(240, 200, 190, 255))
    pop(c, card, W // 2, 1480, t, T(0.3), t1)
    put(c, text_img('gastos com a pele', 'Medium', 30, INK2), W // 2, 1580, window(t, T(0.6), t1), 'c')

def price_tag(txt, sub, color):
    card = shadow_card(400, 300, 40)
    tw = text_img(txt, 'Black', 92, color); card.alpha_composite(tw, (card.width // 2 - tw.width // 2, 100))
    st = text_img(sub, 'Bold', 30, INK2, True, 3); card.alpha_composite(st, (card.width // 2 - st.width // 2, 245))
    return card

def s2(c, t):  # baratinho / caríssimo
    t0, t1 = T(4.70), T(9.45)
    if not (t0 <= t <= t1): return
    words(c, 'Às vezes é um procedimento...', W // 2, 560, t, T(4.92), t1, 74, 'ExtraBold')
    A = price_tag('R$ 99', 'BARATINHO', INK); B = price_tag('R$ 2.900', 'CARÍSSIMO', CLAYD)
    for im, x, y, tt, rot in ((A, 300, 1000, T(5.3), -6), (B, 780, 1230, T(7.4), 5)):
        p = eback((t - tt) / .55); a = window(t, tt, t1, .3)
        if a <= 0: continue
        sw = math.sin((t - tt) * 3.2) * 4 * math.exp(-(t - tt) * 1.2)
        r = im.rotate(rot + sw, resample=Image.BICUBIC, expand=True)
        put(c, r, x, y + (1 - clamp(p)) * -300, a)
        # risco
        q = eo((t - T(8.4)) / .5)
        if q > 0:
            ln = Image.new('RGBA', (W, H), (0, 0, 0, 0))
            ImageDraw.Draw(ln).line((x - 190, y + 40, x - 190 + 380 * q, y - 40), fill=(192, 69, 58, int(230 * a)), width=12)
            c.alpha_composite(ln)
    words(c, 'e nenhum dos dois resolve sozinho.', W // 2, 1600, t, T(8.5), t1, 54, 'SemiBold', INK2)

def calendar(c, t, filled_until, lone=False, a=1.0, cx=W // 2, cy=1080):
    cols, rows, cs, gap = 7, 5, 112, 14
    gw = cols * cs + (cols - 1) * gap; x0 = cx - gw // 2; y0 = cy - (rows * cs + (rows - 1) * gap) // 2
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    for i in range(cols * rows):
        r, k = divmod(i, cols)
        x, y = x0 + k * (cs + gap), y0 + r * (cs + gap)
        on = i < filled_until
        if lone:
            fill = (CLAY + (int(255 * a),)) if i == 0 else (43, 31, 26, int(18 * a))
        else:
            fill = (SAGE + (int(255 * a),)) if on else (43, 31, 26, int(18 * a))
        d.rounded_rectangle((x, y, x + cs, y + cs), 26, fill=fill)
        if (lone and i == 0) or (not lone and on):
            d.line((x + 34, y + 58, x + 50, y + 74), fill=(255, 255, 255, int(255 * a)), width=8)
            d.line((x + 50, y + 74, x + 80, y + 40), fill=(255, 255, 255, int(255 * a)), width=8)
    c.alpha_composite(lay)

def s3(c, t):  # vai uma vez e fica sozinha
    t0, t1 = T(9.45), T(12.80)
    if not (t0 <= t <= t1): return
    words(c, 'Você vai uma vez...', W // 2, 560, t, T(9.70), t1, 92)
    calendar(c, t, 1, True, window(t, T(9.8), t1))
    words(c, 'e fica sozinha.', W // 2, 1560, t, T(11.38), t1, 92, 'ExtraBoldItalic', CLAY)

def s4(c, t):  # acompanhamento diário
    t0, t1 = T(12.80), T(16.80)
    if not (t0 <= t <= t1): return
    words(c, 'Resultado de verdade precisa de', W // 2, 470, t, T(12.9), t1, 54, 'ExtraBold', INK2, max_w=1000)
    words(c, 'acompanhamento', W // 2, 600, t, T(13.9), t1, 112, hi=('acompanhamento',))
    n = int(clamp((t - T(13.4)) / 2.6) * 35)
    calendar(c, t, n, False, window(t, T(13.0), t1))
    st = pill('DIÁRIO', 76, CLAY, WHITE, 'Black', 50, 24)
    pp = clamp((t - T(15.98)) / .35)
    if pp > 0:
        r = st.rotate(-8, resample=Image.BICUBIC, expand=True)
        put(c, r, W // 2 + 180, 1520, window(t, T(15.98), t1, .15), 'c', lerp(1.8, 1.0, eo(pp)))

def s5(c, t):  # alguém do seu lado
    t0, t1 = T(16.80), T(19.50)
    if not (t0 <= t <= t1): return
    p = eio((t - T(16.9)) / 1.2); a = window(t, T(16.9), t1)
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    r = 150; cx = W // 2; cy = 1000
    x1 = lerp(cx - 420, cx - 95, p); x2 = lerp(cx + 420, cx + 95, p)
    d.ellipse((x1 - r, cy - r, x1 + r, cy + r), fill=BLUSH + (int(255 * a),))
    d.ellipse((x2 - r, cy - r, x2 + r, cy + r), fill=CLAY + (int(230 * a),))
    c.alpha_composite(lay)
    put(c, text_img('você', 'Bold', 44, INK), x1, cy, a)
    put(c, text_img('Alê', 'Bold', 44, WHITE), x2, cy, a)
    hp = clamp((t - T(18.0)) / .4)
    if hp > 0:
        s = 1 + .08 * math.sin((t - T(18.0)) * 9)
        put(c, heart(90), cx, cy - 250, a * hp, 'c', s * eback(hp))
    words(c, 'Alguém do seu lado', W // 2, 560, t, T(16.92), t1, 96)
    words(c, 'que veja a sua dor.', W // 2, 1460, t, T(18.0), t1, 92, 'ExtraBoldItalic', CLAY)

@functools.lru_cache(8)
def heart(sz, col=CLAY):
    im = Image.new('RGBA', (sz * 4, sz * 4), (0, 0, 0, 0)); d = ImageDraw.Draw(im); s = sz * 4
    d.ellipse((0, 0, s // 2 + 8, s // 2 + 8), fill=col + (255,)); d.ellipse((s // 2 - 8, 0, s, s // 2 + 8), fill=col + (255,))
    d.polygon([(6, s // 3 + 20), (s - 6, s // 3 + 20), (s // 2, s - 10)], fill=col + (255,))
    return im.resize((sz, sz), Image.LANCZOS)

def s6(c, t):  # aqui comigo: acompanhamento real
    t0, t1 = T(19.50), T(22.75)
    if not (t0 <= t <= t1): return
    a = window(t, T(19.6), t1)
    p = eo((t - T(19.6)) / 1.0)
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    cx, cy, r = W // 2, 820, 180
    d.arc((cx - r, cy - r, cx + r, cy + r), -90, -90 + 360 * p, fill=CLAY + (int(255 * a),), width=6)
    c.alpha_composite(lay)
    put(c, text_img('AM', 'MediumItalic', 150, CLAY), cx, cy, a * clamp((t - T(19.9)) / .5))
    words(c, 'Aqui comigo, você tem', W // 2, 1180, t, T(19.7), t1, 72, 'ExtraBold', INK2)
    words(c, 'acompanhamento real.', W // 2, 1320, t, T(20.9), t1, 84, hi=('real',), max_w=1000)
    q = eo((t - T(21.6)) / .6)
    if q > 0:
        ln = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(ln).rounded_rectangle((180, 1395, 180 + 720 * q, 1409), 7, fill=CLAY + (int(255 * a),))
        c.alpha_composite(ln)

def case_card(n, name, tag):
    card = shadow_card(520, 250, 40)
    d = ImageDraw.Draw(card); pad = 56
    card.alpha_composite(text_img(f'CASO {n:02d}', 'Bold', 26, CLAYD, True, 4), (pad + 30, pad + 26))
    card.alpha_composite(text_img(name, 'Black', 58, INK), (pad + 30, pad + 70))
    card.alpha_composite(pill(tag, 26, BLUSH, CLAYD, 'Bold', 18, 8), (pad + 26, pad + 160))
    return card

def s7(c, t):  # equipe, caso por caso
    t0, t1 = T(22.75), T(28.45)
    if not (t0 <= t <= t1): return
    words(c, 'Eu e a minha equipe olhamos o seu caso', W // 2, 520, t, T(22.9), t1, 76, 'ExtraBold')
    cards = [(case_card(1, 'Ana, 34', 'melasma'), T(23.6), -5, 440), (case_card(2, 'Bia, 27', 'acne e marcas'), T(24.4), 4, 740), (case_card(3, 'Carla, 45', 'firmeza e viço'), T(25.2), -3, 1040)]
    for im, tt, rot, y in cards:
        p = eback((t - tt) / .5); a = window(t, tt, t1, .3)
        r = im.rotate(rot, resample=Image.BICUBIC, expand=True)
        x = W // 2 + (140 if rot > 0 else -60)
        put(c, r, x + (1 - clamp(p)) * 700, y + 380, a)
    words(c, 'um por um.', W // 2, 1690, t, T(25.28), t1, 84, 'ExtraBoldItalic', CLAY)

def phone(t, t_msg, name='Mariana'):
    w, h = 470, 900
    im = Image.new('RGBA', (w + 80, h + 80), (0, 0, 0, 0))
    sh = Image.new('RGBA', im.size, (0, 0, 0, 0)); ImageDraw.Draw(sh).rounded_rectangle((40, 58, 40 + w, 58 + h), 70, fill=(60, 30, 20, 90))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(22)))
    d = ImageDraw.Draw(im)
    d.rounded_rectangle((40, 40, 40 + w, 40 + h), 70, fill=INK + (255,))
    d.rounded_rectangle((54, 54, 26 + w, 26 + h), 58, fill=(239, 231, 221, 255))
    d.rounded_rectangle((54, 54, 26 + w, 190), 58, fill=WADARK + (255,)); d.rectangle((54, 140, 26 + w, 190), fill=WADARK + (255,))
    d.ellipse((80, 100, 140, 160), fill=PORC + (255,))
    im.alpha_composite(text_img('AM', 'Bold', 24, INK), (90, 112))
    im.alpha_composite(text_img('Alê · Estética facial', 'Bold', 26, WHITE), (152, 100))
    im.alpha_composite(text_img('online', 'Medium', 22, (210, 235, 225)), (152, 134))
    msgs = [(t_msg, f'Oi, {name}! Que alegria te receber aqui', True),
            (t_msg + .7, 'Vi a sua análise: o seu melasma tem jeito, e eu vou cuidar dele com você.', True),
            (t_msg + 1.4, 'Separei quinta, 14h, em Águas Claras. Pode ser?', True)]
    y = 230
    for tt, txt, alê in msgs:
        if t < tt: break
        lines, _, lh = words_layout(txt, 28, 'Medium', 330)
        bh = int(len(lines) * 36 + 34)
        p = eo((t - tt) / .35)
        bub = rrect(370, bh, 22, (255, 255, 255, 255))
        bd = ImageDraw.Draw(bub)
        for li, (ws, _) in enumerate(lines):
            bd.text((20, 14 + li * 36), ' '.join(ws), font=font('Medium', 28), fill=INK + (255,))
        im.alpha_composite(with_alpha(bub, p), (76, int(y + (1 - p) * 30)))
        y += bh + 16
    return im

def feature(c, t, tt, t1, idx, title, sub, y):
    a = window(t, tt, t1, .35); p = eo((t - tt) / .5)
    if a <= 0: return
    card = shadow_card(860, 210, 44)
    num = pill(f'0{idx}', 30, CLAY, WHITE, 'Bold', 20, 10, True)
    card.alpha_composite(num, (100, 90))
    card.alpha_composite(text_img(title, 'Black', 54, INK), (210, 72))
    card.alpha_composite(text_img(sub, 'Medium', 30, INK2), (214, 150))
    put(c, card, W // 2 + (1 - p) * 300, y, a)

def s8(c, t):  # o sistema
    t0, t1 = T(28.45), T(37.10)
    if not (t0 <= t <= t1): return
    label(c, 'Por isso criamos', W // 2, 400, t, T(28.64), t1)
    words(c, 'todo um sistema para te receber', W // 2, 530, t, T(28.9), t1, 84, hi=('sistema',))
    # análise com IA
    a = window(t, T(29.6), t1)
    if a > 0:
        fc = shadow_card(560, 640, 60, (214, 160, 132))
        put(c, fc, 345, 1040, a * clamp((t - T(29.6)) / .4))
        mesh(c, 345, 1040, 1.9, clamp((t - T(29.9)) / 2.2), WHITE, a)
        put(c, pill('ANÁLISE COM IA', 26, WHITE, CLAYD, 'Bold', 20, 10, True), 345, 1330, a * clamp((t - T(31.84)) / .4))
    # rotina
    a2 = window(t, T(33.48), t1)
    if a2 > 0:
        card = shadow_card(400, 380, 40)
        dd = ImageDraw.Draw(card)
        card.alpha_composite(text_img('Sua rotina', 'Black', 44, INK), (90, 86))
        for i, it in enumerate(['Limpeza suave', 'Vitamina C', 'Protetor com cor', 'Manutenção']):
            q = clamp((t - T(33.7) - i * .25) / .3)
            if q <= 0: continue
            yy = 160 + i * 58
            dd.rounded_rectangle((90, yy, 120, yy + 30), 8, fill=SAGE + (int(255 * q),))
            card.alpha_composite(with_alpha(text_img(it, 'Medium', 32, INK2), q), (136, yy - 8))
        put(c, card, 790, 900 + (1 - eo((t - T(33.48)) / .5)) * 80, a2)
    # WhatsApp
    a3 = window(t, T(35.4), t1)
    if a3 > 0:
        ph = phone(t, T(35.9))
        put(c, ph, 790, 1450 + (1 - eo((t - T(35.4)) / .6)) * 300, a3, 'c', .62)
        put(c, pill('SUPORTE NO WHATSAPP', 24, WA, (7, 59, 30), 'Bold', 18, 10, True), 790, 1770, a3)

def s9(c, t):  # não é para vender produto
    t0, t1 = T(37.10), T(39.60)
    if not (t0 <= t <= t1): return
    words(c, 'A gente não está aqui para', W // 2, 840, t, T(37.3), t1, 66, 'ExtraBold', INK2, max_w=1000)
    words(c, 'vender produto.', W // 2, 1000, t, T(38.2), t1, 112)
    q = eo((t - T(38.9)) / .4)
    if q > 0:
        ln = Image.new('RGBA', (W, H), (0, 0, 0, 0))
        ImageDraw.Draw(ln).rounded_rectangle((150, 990, 150 + 780 * q, 1012), 10, fill=(192, 69, 58, int(240 * window(t, T(38.9), t1))))
        c.alpha_composite(ln)

def s10(c, t):  # sentir bem, autoestima, confiar
    t0, t1 = T(39.60), T(46.35)
    if not (t0 <= t <= t1): return
    label(c, 'Estamos aqui para você', W // 2, 470, t, T(39.72), t1)
    items = [('voltar a se sentir bem', T(40.4), 760), ('recuperar a sua autoestima', T(42.6), 1040), ('confiar de novo na estética', T(44.2), 1320)]
    for txt, tt, y in items:
        card = shadow_card(900, 200, 50)
        tw = text_img(txt, 'Black', 64, INK)
        card.alpha_composite(tw, (card.width // 2 - tw.width // 2, card.height // 2 - tw.height // 2))
        p = clamp((t - tt) / .5); a = window(t, tt, t1, .3)
        put(c, card, W // 2, y, a, 'c', lerp(.8, 1, eback(p)))
    hp = clamp((t - T(45.2)) / .4)
    if hp > 0: put(c, heart(110), W // 2, 1600, hp * window(t, T(45.2), t1), 'c', (1 + .06 * math.sin(t * 8)) * eback(hp))

def s11(c, t):  # pare de gastar / vem ser cuidada
    t0, t1 = T(46.35), T(50.75)
    if not (t0 <= t <= t1): return
    words(c, 'Pare de gastar com o que não funciona.', W // 2, 640, t, T(46.48), t1, 76, 'ExtraBold', INK2)
    words(c, 'Vem ser cuidada de verdade.', W // 2, 1060, t, T(48.92), t1, 128, hi=('cuidada',))
    for i in range(10):
        ang = i / 10 * math.tau + t * .5; rr = 470 + 30 * math.sin(t * 2 + i)
        q = window(t, T(49.1) + i * .05, t1)
        put(c, sparkle(26 if i % 2 else 18), W // 2 + math.cos(ang) * rr, 1060 + math.sin(ang) * rr * .7, q)

@functools.lru_cache(8)
def sparkle(sz):
    s = sz * 4; im = Image.new('RGBA', (s, s), (0, 0, 0, 0)); d = ImageDraw.Draw(im); m = s // 2
    d.polygon([(m, 0), (m + s // 9, m - s // 9), (s, m), (m + s // 9, m + s // 9), (m, s), (m - s // 9, m + s // 9), (0, m), (m - s // 9, m - s // 9)], fill=CLAY + (255,))
    return im.resize((sz, sz), Image.LANCZOS)

def s12(c, t):  # final
    t0 = T(50.75)
    if t < t0: return
    a = clamp((t - t0) / .5)
    words(c, 'Eu espero cuidar de você em breve.', W // 2, 380, t, T(50.86), DUR + 5, 60, 'SemiBoldItalic', CLAYD)
    card = shadow_card(900, 1120, 70)
    put(c, card, W // 2, 1090, a, 'c', lerp(.92, 1, eo((t - t0) / .6)))
    yb = 1090 - 560
    lay = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(lay)
    p = eo((t - T(51.0)) / .9)
    d.arc((W // 2 - 110, yb + 100, W // 2 + 110, yb + 320), -90, -90 + 360 * p, fill=CLAY + (int(255 * a),), width=5)
    c.alpha_composite(lay)
    put(c, text_img('AM', 'MediumItalic', 96, CLAY), W // 2, yb + 210, a)
    rise(c, text_img('Alessandra Mendes', 'Black', 76, INK), W // 2, yb + 400, t, T(51.2), DUR + 5)
    rise(c, text_img('ESTÉTICA FACIAL · PELE · MELASMA', 'Bold', 26, INK2, True, 5), W // 2, yb + 480, t, T(51.4), DUR + 5, dy=20)
    pop(c, pill('Glass Skin', 34, BLUSH, CLAYD, 'Bold'), W // 2 - 170, yb + 590, t, T(51.8), DUR + 5)
    pop(c, pill('Protocolo AM', 34, BLUSH, CLAYD, 'Bold'), W // 2 + 170, yb + 590, t, T(52.0), DUR + 5)
    rise(c, text_img('Águas Claras · DF   |   Setor Marista · Goiânia', 'SemiBold', 34, INK2), W // 2, yb + 690, t, T(52.3), DUR + 5, dy=20)
    btn = pill('(61) 99114-0713  ·  WhatsApp', 44, WA, (7, 59, 30), 'Black', 44, 26)
    s = 1 + .03 * math.sin((t - T(52.6)) * 5) if t > T(53.2) else 1
    pp = clamp((t - T(52.6)) / .45)
    if pp > 0: put(c, btn, W // 2, yb + 830, pp, 'c', s * lerp(1.2, 1, eback(pp)))
    rise(c, text_img('Faça sua análise de pele grátis', 'Bold', 36, CLAYD), W // 2, yb + 960, t, T(53.2), DUR + 5, dy=20)

SCENES = [s1, s2, s3, s4, s5, s6, s7, s8, s9, s10, s11, s12]

def frame(t):
    c = background(t)
    topbar(c, t)
    for s in SCENES: s(c, t)
    a_out = clamp((t - (DUR - .6)) / .6)
    if a_out > 0: c.alpha_composite(Image.new('RGBA', (W, H), PORC + (int(255 * a_out),)))
    return c.convert('RGB')

def render_range(f0, f1, path):
    p = subprocess.Popen(['ffmpeg', '-y', '-v', 'error', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-',
                          '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', path], stdin=subprocess.PIPE)
    for f in range(f0, f1):
        p.stdin.write(frame(f / FPS).tobytes())
    p.stdin.close(); p.wait()

if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    if sys.argv[1] == 'still':
        for v in sys.argv[2:]:
            frame(float(v)).save(os.path.join(OUT, f'still_{v}.png'))
    else:
        k, n = int(sys.argv[1]), int(sys.argv[2])
        total = int(DUR * FPS); per = math.ceil(total / n)
        render_range(k * per, min(total, (k + 1) * per), os.path.join(OUT, f'chunk_{k:02d}.mp4'))
