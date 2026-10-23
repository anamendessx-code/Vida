"""Motion video renderer: LÍDERES DO BRASIL × ADRIANO AMARAL (1080x1920, 30fps).

usage: python3 render.py <chunk_index> <n_chunks>   -> out/chunk_XX.mp4
       python3 render.py still <t> [t ...]           -> out/still_<t>.png
"""
import os, sys, math, subprocess, functools, json
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

S = os.path.dirname(os.path.abspath(__file__))
W, H, FPS = 1080, 1920, 30
DUR = 118.5

WHITE = (255, 255, 255)
INDIGO = (66, 75, 149)
ACCENT = (110, 128, 255)
SOFT = (190, 198, 255)
NAVY = (7, 9, 26)

FD = '/usr/share/fonts/opentype/inter/InterDisplay-'


# ----------------------------------------------------------------- helpers
def clamp(x, a=0.0, b=1.0):
    return a if x < a else b if x > b else x

def eo(p):  # ease out cubic
    p = clamp(p); return 1 - (1 - p) ** 3

def ei(p):
    p = clamp(p); return p ** 3

def eio(p):
    p = clamp(p); return 4 * p ** 3 if p < .5 else 1 - (-2 * p + 2) ** 3 / 2

def eback(p):
    p = clamp(p); c1 = 1.70158; c3 = c1 + 1
    return 1 + c3 * (p - 1) ** 3 + c1 * (p - 1) ** 2

def lerp(a, b, p):
    return a + (b - a) * p

@functools.lru_cache(None)
def font(weight, size):
    return ImageFont.truetype(FD + weight + '.otf', int(size))

PAD = 26

@functools.lru_cache(4096)
def text_img(txt, weight='Black', size=100, color=WHITE, tracking=0, shadow=0.55, alpha=255):
    f = font(weight, size)
    asc, desc = f.getmetrics()
    if tracking:
        wid = sum(f.getlength(ch) for ch in txt) + tracking * (len(txt) - 1)
    else:
        wid = f.getlength(txt)
    w, h = int(math.ceil(wid)) + 2 * PAD, asc + desc + 2 * PAD
    im = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    if tracking:
        x = PAD
        for ch in txt:
            d.text((x, PAD), ch, font=f, fill=color + (alpha,))
            x += f.getlength(ch) + tracking
    else:
        d.text((PAD, PAD), txt, font=f, fill=color + (alpha,))
    if shadow:
        a = im.getchannel('A').filter(ImageFilter.GaussianBlur(max(4, size / 9)))
        a = a.point([int(v * shadow) for v in range(256)])
        sh = Image.new('RGBA', (w, h), (0, 0, 0, 0)); sh.putalpha(a)
        sh.alpha_composite(im)
        im = sh
    return im

def fit(txt, weight, max_w, max_size, tracking=0, **kw):
    size = max_size
    while size > 18:
        f = font(weight, size)
        wid = (sum(f.getlength(c) for c in txt) + tracking * (len(txt) - 1)) if tracking else f.getlength(txt)
        if wid <= max_w: break
        size -= 2
    return text_img(txt, weight, size, tracking=tracking, **kw)

def alpha_img(im, a):
    a = round(clamp(a), 2)
    if a >= 0.999: return im
    out = im.copy()
    out.putalpha(im.getchannel('A').point([int(v * a) for v in range(256)]))
    return out

def put(c, im, x, y, a=1.0, anchor='c'):
    """anchor 'c': x,y = center; 'l': x = left edge of glyphs, y = center; 't': x center, y top of glyph box."""
    if a <= 0.01: return
    if anchor == 'c':
        px, py = x - im.width / 2, y - im.height / 2
    elif anchor == 'l':
        px, py = x - PAD, y - im.height / 2
    else:
        px, py = x - im.width / 2, y - PAD
    c.alpha_composite(alpha_img(im, a), (int(round(px)), int(round(py))))

def reveal(c, im, x, y, t, t0, t1=None, dur=0.55, anchor='c', out_dur=0.35, a=1.0):
    """Masked slide-up reveal; optional slide-up exit at t1."""
    if t < t0: return
    if t1 is not None and t >= t1 + out_dur: return
    p = eo((t - t0) / dur)
    off = (1 - p) * im.height * 0.85
    alpha = clamp((t - t0) / (dur * 0.6))
    if t1 is not None and t > t1:
        q = ei((t - t1) / out_dur)
        off = -q * im.height * 0.7
        alpha = 1 - q
    if anchor == 'c':
        bx, by = x - im.width / 2, y - im.height / 2
    elif anchor == 'l':
        bx, by = x - PAD, y - im.height / 2
    else:
        bx, by = x - im.width / 2, y - PAD
    hh = im.height
    o = int(round(off))
    sy0 = max(0, -o); dy = by + max(0, o); hgt = hh - abs(o)
    if hgt <= 2: return
    crop = im.crop((0, sy0, im.width, sy0 + hgt))
    c.alpha_composite(alpha_img(crop, alpha * a), (int(round(bx)), int(round(dy))))

def pop(c, im, x, y, t, t0, t1=None, dur=0.45, s0=1.35, out_dur=0.3):
    if t < t0: return
    if t1 is not None and t >= t1 + out_dur: return
    p = eo((t - t0) / dur)
    s = lerp(s0, 1.0, p); a = clamp((t - t0) / (dur * 0.5))
    if t1 is not None and t > t1:
        q = ei((t - t1) / out_dur); s = lerp(1.0, 0.85, q); a = 1 - q
    if abs(s - 1) > 0.005:
        im = im.resize((max(1, int(im.width * s)), max(1, int(im.height * s))), Image.BILINEAR)
    put(c, im, x, y, a)

def fade_in_out(t, t0, t1, din=0.4, dout=0.35):
    if t < t0 or t > t1 + dout: return 0.0
    return min(clamp((t - t0) / din), 1 - clamp((t - t1) / dout))

def hbar(c, x, y, length, thick, color, a=1.0, anchor='l'):
    if length < 1 or a <= 0.01: return
    if anchor == 'c': x = x - length / 2
    ov = Image.new('RGBA', (int(length), int(thick)), color + (int(255 * a),))
    c.alpha_composite(ov, (int(x), int(y - thick / 2)))

@functools.lru_cache(256)
def rrect(w, h, r, fill, outline=None, ow=0):
    im = Image.new('RGBA', (int(w), int(h)), (0, 0, 0, 0))
    ImageDraw.Draw(im).rounded_rectangle((0, 0, w - 1, h - 1), r, fill=fill, outline=outline, width=ow)
    return im

@functools.lru_cache(256)
def pill(txt, size=34, fill=ACCENT + (235,), color=WHITE, weight='Bold', tracking=3, padx=30, pady=16, outline=None):
    ti = text_img(txt, weight, size, color, tracking=tracking, shadow=0)
    f = font(weight, size); asc, desc = f.getmetrics()
    tw = ti.width - 2 * PAD
    w, h = tw + 2 * padx, asc + 2 * pady - 4
    bg = rrect(w, h, h // 2, fill, outline, 3 if outline else 0).copy()
    bg.alpha_composite(ti, (padx - PAD, pady - PAD - int(desc * 0.2) - 2))
    return bg

def dots(c, y, cur, a=1.0, n=8):
    gap = 34; total = (n - 1) * gap + 40
    x = W / 2 - total / 2
    for i in range(n):
        if i == cur:
            put(c, rrect(52, 14, 7, ACCENT + (255,)), x + 26, y, a); x += 52 + 22
        else:
            col = (255, 255, 255, 200) if i < cur else (255, 255, 255, 80)
            put(c, rrect(14, 14, 7, col), x + 7, y, a); x += 14 + 20


# ----------------------------------------------------------------- assets
LOGO = Image.open(os.path.join(S, 'assets/logo_circle.png')).convert('RGBA')
SYMBOL = Image.open(os.path.join(S, 'assets/logo_symbol.png')).convert('RGBA')

@functools.lru_cache(64)
def logo_sized(sz, which='logo'):
    src = LOGO if which == 'logo' else SYMBOL
    return src.resize((sz, sz), Image.LANCZOS)

def make_vignette():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    nx, ny = (xx - W / 2) / (W / 2), (yy - H / 2) / (H / 2)
    r = np.sqrt(nx ** 2 * 0.9 + ny ** 2 * 0.55)
    v = 1 - 0.55 * np.clip(r - 0.45, 0, 1) ** 1.6
    top = np.clip(1 - (yy / 420), 0, 1) ** 2 * 0.45
    bot = np.clip((yy - 1450) / 470, 0, 1) ** 1.5 * 0.55
    v = v * (1 - top) * (1 - bot)
    return Image.fromarray((np.clip(v, 0, 1) * 255).astype(np.uint8), 'L')
VIG = make_vignette()
BLACK = Image.new('RGB', (W, H), (0, 0, 0))

def make_grid():
    im = Image.new('RGBA', (W, H + 90), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    for x in range(0, W + 1, 90):
        d.line((x, 0, x, H + 90), fill=(140, 155, 255, 26), width=1)
    for y in range(0, H + 90, 90):
        d.line((0, y, W, y), fill=(140, 155, 255, 26), width=1)
    for x in range(0, W + 1, 90):
        for y in range(0, H + 90, 90):
            d.ellipse((x - 2, y - 2, x + 2, y + 2), fill=(170, 180, 255, 70))
    return im
GRID = make_grid()

def make_final_bg():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((xx - W / 2) / W) ** 2 + ((yy - 680) / H) ** 2)
    g = np.clip(1 - d * 1.9, 0, 1) ** 1.8
    base = np.array(NAVY, np.float32)
    glow = np.array((52, 62, 150), np.float32)
    img = base[None, None, :] * (1 - g[..., None]) + glow[None, None, :] * g[..., None]
    return Image.fromarray(img.clip(0, 255).astype(np.uint8), 'RGB')
FINAL_BG = make_final_bg()

def make_rings():
    im = Image.new('RGBA', (1400, 1400), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse((2, 2, 1397, 1397), outline=(140, 155, 255, 255), width=4)
    return im
RING = make_rings()

@functools.lru_cache(8)
def glow_disc(sz):
    im = Image.new('RGBA', (sz, sz), (0, 0, 0, 0))
    ImageDraw.Draw(im).ellipse((sz * .25, sz * .25, sz * .75, sz * .75), fill=ACCENT + (170,))
    return im.filter(ImageFilter.GaussianBlur(sz / 10))


# ----------------------------------------------------------------- grading
def grade_lut(dim):
    x = np.arange(256) / 255.0
    curve = x + 0.10 * np.sin((x - 0.5) * 2 * np.pi) * -0.5 * 0 + 0.0
    curve = np.clip((x - 0.5) * 1.12 + 0.5, 0, 1)            # contrast
    r = np.clip(curve * 0.97, 0, 1); g = np.clip(curve * 0.99, 0, 1)
    b = np.clip(curve * 1.02 + 0.025 * (1 - x), 0, 1)          # cool shadows
    lut = []
    for ch in (r, g, b):
        lut += [int(v * dim * 255) for v in ch]
    return lut

@functools.lru_cache(128)
def lut_for(dim_q):
    return grade_lut(dim_q / 100)


# ----------------------------------------------------------------- sources
class Reader:
    def __init__(self, clip, ss, speed):
        p60 = os.path.join(S, 'src60', clip + '.mp4')
        self.sfps = 60 if os.environ.get('USE60') and os.path.exists(p60) else 30
        path = p60 if self.sfps == 60 else os.path.join(S, 'src', clip + '.mp4')
        self.speed = speed
        self.proc = subprocess.Popen(
            ['ffmpeg', '-v', 'error', '-ss', f'{ss:.3f}', '-i', path, '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'],
            stdout=subprocess.PIPE, bufsize=W * H * 3 * 2)
        self.idx = -1; self.cur = None

    def get(self, i):
        want = int(round(i * self.speed * self.sfps / FPS))
        while self.idx < want:
            buf = self.proc.stdout.read(W * H * 3)
            if len(buf) < W * H * 3: break
            self.cur = buf; self.idx += 1
        return Image.frombuffer('RGB', (W, H), self.cur, 'raw', 'RGB', 0, 1)

    def close(self):
        try: self.proc.kill()
        except Exception: pass


def kb_frame(img, z, px, py, box_w=W, box_h=H, out=(W, H), cx=None, cy=None):
    cw, ch = box_w / z, box_h / z
    if cx is None:
        cx = W / 2 + px * (W - cw) / 2
        cy = H / 2 + py * (H - ch) / 2
    cx = clamp(cx, cw / 2, W - cw / 2); cy = clamp(cy, ch / 2, H - ch / 2)
    return img.resize(out, Image.BILINEAR, box=(cx - cw / 2, cy - ch / 2, cx + cw / 2, cy + ch / 2))


# ----------------------------------------------------------------- timeline (edit seconds)
def L(clip, ss, sp, z=(1.0, 1.08), px=(0, 0), py=(0, 0)):
    return dict(clip=clip, ss=ss, sp=sp, z=z, px=px, py=py)

SEGS = [
    # S1 — abertura
    dict(t0=0.00, t1=3.90, l=L('7772', 0.2, 0.75, (1.14, 1.0), (0.2, -0.1)), dim=0.6, fadein=0.9, flash=False),
    dict(t0=3.90, t1=5.90, l=L('7769', 0.5, 0.8, (1.0, 1.1), (0, 0), (-0.3, -0.3)), dim=0.72),
    dict(t0=5.90, t1=8.20, l=L('7768', 2.0, 0.8, (1.12, 1.0), (0.1, 0.1), (-0.3, -0.3)), dim=0.72),
    dict(t0=8.20, t1=11.05, l=L('7769', 5.0, 0.8, (1.0, 1.1), (0, 0), (-0.3, -0.3)), dim=0.8),
    # S2 — apresentação
    dict(t0=11.05, t1=13.50, l=L('7772', 6.0, 0.75, (1.32, 1.2), (0.55, 0.5), (0.2, 0.15)), dim=0.82),
    dict(t0=13.50, t1=15.60, l=L('7771', 2.5, 0.8, (1.06, 1.16), (0, 0), (-0.2, -0.25)), dim=0.82),
    dict(t0=15.60, t1=19.75, split=(L('7772_2', 1.6, 0.6, (1.0, 1.08)), L('7771', 5.0, 0.6, (1.0, 1.08))),
         fy=(900, 790), dim=0.8),
    # S3 — estrutura
    dict(t0=19.75, t1=22.50, l=L('7774', 0.0, 0.85, (1.0, 1.12), (0.25, 0.25), (-0.1, -0.1)), dim=0.55, blur=2),
    dict(t0=22.50, t1=29.20, l=L('7774', 2.6, 0.49, (1.05, 1.28), (0, 0), (-0.05, -0.05)), dim=0.42, blur=4),
    dict(t0=29.20, t1=37.85, l=L('7772', 5.0, 0.7, (1.22, 1.1), (0.5, 0.45), (0.25, 0.2)), dim=0.48, blur=3),
    dict(t0=37.85, t1=47.05, l=L('7772_2', 0.0, 0.5, (1.0, 1.12), (0, 0), (0, -0.2)), dim=0.48, blur=3),
    dict(t0=47.05, t1=56.95, l=L('7772', 0.0, 0.48, (1.06, 1.16), (-0.4, 0.4), (0, 0)), dim=0.48, blur=3),
    # S4 — nova geração
    dict(t0=56.95, t1=61.85, l=L('7774', 3.0, 0.58, (1.3, 1.1), (0, 0), (-0.05, -0.05)), dim=0.42, blur=3, grid=True),
    dict(t0=61.85, t1=67.20, l=L('7769', 0.0, 1.0, (1.1, 1.2)), dim=0.36, blur=12, grid=True, tint=True),
    dict(t0=67.20, t1=71.45, l=L('7768', 0.0, 1.0, (1.1, 1.2)), dim=0.36, blur=12, grid=True, tint=True),
    dict(t0=71.45, t1=75.95, l=L('7771', 0.0, 1.0, (1.1, 1.2)), dim=0.36, blur=12, grid=True, tint=True),
    dict(t0=75.95, t1=80.70, l=L('7768', 4.3, 0.95, (1.1, 1.2)), dim=0.36, blur=12, grid=True, tint=True),
    dict(t0=80.70, t1=84.60, l=L('7769', 4.3, 1.0, (1.1, 1.2)), dim=0.36, blur=12, grid=True, tint=True),
    # S5 — conexão
    dict(t0=84.60, t1=85.55, l=L('7768', 1.0, 1.0, (1.18, 1.05), (0, 0), (-0.3, -0.3)), dim=0.55),
    dict(t0=85.55, t1=86.85, l=L('7769', 1.5, 1.0, (1.18, 1.05), (0, 0), (-0.2, -0.2)), dim=0.55),
    dict(t0=86.85, t1=87.50, l=L('7771', 3.0, 1.0, (1.18, 1.05), (0, 0), (-0.3, -0.3)), dim=0.55),
    dict(t0=87.50, t1=88.75, l=L('7774', 0.2, 1.0, (1.25, 1.1), (0.4, 0.4), (-0.2, -0.2)), dim=0.55),
    dict(t0=88.75, t1=89.90, l=L('7772', 8.5, 1.0, (1.35, 1.2), (0.3, 0.3), (0.2, 0.2)), dim=0.55),
    dict(t0=89.90, t1=90.95, l=L('7768', 6.5, 1.0, (1.18, 1.05), (0, 0), (-0.3, -0.3)), dim=0.55),
    dict(t0=90.95, t1=95.30, l=L('7769', 1.0, 0.75, (1.0, 1.12), (0, 0), (-0.35, -0.35)), dim=0.62),
    dict(t0=95.30, t1=99.60, l=L('7768', 5.9, 0.7, (1.0, 1.12), (0, 0), (-0.35, -0.35)), dim=0.62),
    # S6 — clímax
    dict(t0=99.60, t1=101.00, l=L('7772_2', 2.3, 0.6, (1.25, 1.12), (-0.3, -0.3), (0.0, 0.0)), dim=0.55),
    dict(t0=101.00, t1=102.30, l=L('7771', 3.0, 0.6, (1.25, 1.12), (0, 0), (-0.35, -0.35)), dim=0.55),
    dict(t0=102.30, t1=103.65, l=L('7769', 2.0, 0.6, (1.25, 1.12), (0, 0), (-0.35, -0.35)), dim=0.55),
    dict(t0=103.65, t1=108.10, l=L('7774', 0.3, 0.45, (1.0, 1.4), (0.3, 0.35), (-0.15, -0.25)), dim=(0.5, 0.0), blur=(0, 14)),
    # FINAL
    dict(t0=108.10, t1=DUR + 0.01, final=True),
]
SECTION_STARTS = [0.0, 11.05, 19.75, 56.95, 84.60, 99.60, 108.10]


def seg_at(T):
    for i, s in enumerate(SEGS):
        if s['t0'] <= T < s['t1']: return i
    return len(SEGS) - 1

def ramp(v, p):
    return lerp(v[0], v[1], p) if isinstance(v, tuple) else v


class BG:
    def __init__(self):
        self.cur = None; self.readers = []

    def frame(self, T):
        i = seg_at(T); s = SEGS[i]
        if self.cur != i:
            for r in self.readers: r.close()
            self.cur = i
            if 'l' in s: self.readers = [Reader(s['l']['clip'], s['l']['ss'], s['l']['sp'])]
            elif 'split' in s: self.readers = [Reader(l['clip'], l['ss'], l['sp']) for l in s['split']]
            else: self.readers = []
        dur = s['t1'] - s['t0']; tau = T - s['t0']; p = clamp(tau / dur)
        fi = int(round(tau * FPS))
        # transition punch on cut
        punch = 1.0
        if s.get('flash', True) and tau < 0.3:
            punch = 1 + 0.07 * (1 - eo(tau / 0.3))
        if s.get('final'):
            img = FINAL_BG.copy()
        elif 'l' in s:
            l = s['l']; src = self.readers[0].get(fi)
            z = lerp(*l['z'], eio(p)) * punch
            img = kb_frame(src, z, lerp(*l['px'], eio(p)), lerp(*l['py'], eio(p)))
        else:
            img = Image.new('RGB', (W, H))
            for k, (l, r) in enumerate(zip(s['split'], self.readers)):
                src = r.get(fi)
                z = lerp(*l['z'], eio(p)) * punch
                part = kb_frame(src, z, 0, 0, W, H / 2, (W, H // 2), cx=W / 2, cy=s['fy'][k])
                # slide-in of each half
                sl = eo((tau - 0.0 - k * 0.12) / 0.5)
                dx = int((1 - sl) * (W if k == 0 else -W))
                img.paste(part, (dx, k * H // 2))
        blur = ramp(s.get('blur', 0), p)
        if blur > 0.5:
            small = img.resize((W // 4, H // 4), Image.BILINEAR).filter(ImageFilter.GaussianBlur(blur / 4))
            img = small.resize((W, H), Image.BILINEAR)
        if not s.get('final'):
            dim = ramp(s.get('dim', 1.0), eio(p) if isinstance(s.get('dim'), tuple) else p)
            if s.get('fadein'): dim *= eo(tau / s['fadein'])
            img = img.point(lut_for(int(round(dim * 100))))
            if s.get('tint'):
                img = Image.blend(img, Image.new('RGB', (W, H), (25, 30, 90)), 0.35)
            img = Image.composite(img, BLACK, VIG)
        c = img.convert('RGBA')
        if s.get('grid'):
            off = int((T * 40) % 90)
            c.alpha_composite(GRID.crop((0, off, W, off + H)))
        return c, s, tau


# ----------------------------------------------------------------- overlays
def ov_s1(c, t):
    name_tag(c, t, 0.9, 3.55, 'CLÁUDIA', 'VICE-PRESIDENTE · LÍDERES DO BRASIL')
    name_tag(c, t, 4.05, 5.65, 'PEDRO', 'SÓCIO · LÍDERES DO BRASIL')
    name_tag(c, t, 6.05, 7.95, 'DAHER', 'PRESIDENTE · LÍDERES DO BRASIL')
    if t < 4.2:
        reveal(c, fit('GRANDES NEGÓCIOS', 'Black', 960, 118), W / 2, 760, t, 0.55, 3.55)
        reveal(c, text_img('COMEÇAM COM', 'Light', 62, tracking=14), W / 2, 885, t, 1.55, 3.6)
        reveal(c, fit('GRANDES CONEXÕES', 'Black', 960, 118, color=SOFT), W / 2, 1000, t, 2.45, 3.65)
        if 2.8 < t < 4.0:
            ln = eo((t - 2.8) / 0.6) * 260 * (1 - ei((t - 3.6) / 0.3))
            hbar(c, W / 2, 1110, ln, 6, ACCENT, anchor='c')
    if 3.9 <= t < 8.4:
        reveal(c, text_img('E HOJE,', 'Medium', 46, SOFT, tracking=10), W / 2, 1140, t, 4.15, 8.0)
        reveal(c, fit('OS LÍDERES DO BRASIL', 'Black', 960, 100), W / 2, 1235, t, 5.0, 8.0)
        reveal(c, text_img('TIVERAM UM ENCONTRO', 'Light', 54, tracking=6), W / 2, 1340, t, 5.95, 8.05)
        reveal(c, fit('MUITO ESPECIAL', 'Black', 960, 92, color=SOFT), W / 2, 1430, t, 7.05, 8.05)

def lower_third(c, t, t0, t1, name, role):
    if t < t0 or t > t1 + 0.4: return
    a = fade_in_out(t, t0, t1, 0.3, 0.35)
    bh = eo((t - t0) / 0.4) * 150
    hbar(c, 70, 1310, 8, bh, ACCENT, a)  # vertical bar via thick narrow box
    reveal(c, text_img(name, 'Black', 66), 104, 1272, t, t0 + 0.1, t1, anchor='l')
    p = pill(role, 34, tracking=8)
    reveal(c, p, 104 + p.width / 2, 1356, t, t0 + 0.3, t1)

def ov_s2(c, t):
    if 11.05 <= t < 15.9:
        reveal(c, fit('DUAS GERAÇÕES.', 'Black', 940, 112), W / 2, 330, t, 11.1, 15.45)
        reveal(c, text_img('UMA HISTÓRIA', 'Light', 54, SOFT, tracking=14), W / 2, 445, t, 12.6, 15.45)
    if 15.6 <= t < 19.9:
        # seam band
        a = fade_in_out(t, 15.75, 19.5, 0.3, 0.3)
        bw = eo((t - 15.75) / 0.5) * W
        hbar(c, W / 2, H / 2, bw, 150, (12, 14, 40), 0.82 * a, anchor='c')
        hbar(c, W / 2, H / 2 - 75, bw, 4, ACCENT, a, anchor='c')
        hbar(c, W / 2, H / 2 + 75, bw, 4, ACCENT, a, anchor='c')
        words = [(15.85, 16.15, 'EMPREENDEDORISMO'), (16.15, 17.3, 'VISÃO EMPRESARIAL'), (17.3, 19.45, 'GRANDES NEGÓCIOS')]
        for k, (a0, a1, wd) in enumerate(words):
            reveal(c, fit(wd, 'Black', 900, 84), W / 2, H / 2, t, a0, a1 - 0.18 if k < 2 else a1, dur=0.35, out_dur=0.18)

COMPANIES = ['Arthur D. Little', 'Magna Capital', 'ITEC', 'IDEA Corporate Minority Holdings',
             'Nia', 'Oasis Cloud', 'VennTure Capital', 'Engemega']

def ov_s3_intro(c, t):
    if not (19.75 <= t < 29.5): return
    T_UP = 24.6
    up = eio((t - T_UP) / 0.7) if t > T_UP else 0
    y0 = lerp(0, -330, up)
    reveal(c, text_img('POR TRÁS DESSA HISTÓRIA', 'Medium', 38, SOFT, tracking=10), W / 2, 560 + y0, t, 19.85, 28.9)
    reveal(c, text_img('IDEA', 'Black', 230), W / 2, 720 + y0, t, 21.2, 28.95)
    reveal(c, text_img('HOLDING', 'Light', 70, tracking=40), W / 2, 870 + y0, t, 21.45, 29.0)
    if t < T_UP + 0.3:
        reveal(c, text_img('ESTRUTURA EMPRESARIAL', 'SemiBold', 44, tracking=4), W / 2, 1010, t, 21.9, T_UP - 0.2)
        reveal(c, text_img('DIVERSIFICADA', 'SemiBold', 44, SOFT, tracking=4), W / 2, 1070, t, 22.6, T_UP - 0.2)
    if t > T_UP:
        hub_y = 940 + 0
        # network
        a_all = 1 - clamp((t - 28.85) / 0.35)
        hub = eo((t - T_UP - 0.2) / 0.4)
        put(c, glow_disc(160), W / 2, 625, a_all * hub)
        put(c, rrect(22, 22, 11, ACCENT + (255,)), W / 2, 625, a_all * hub)
        cols = [W / 2 - 245, W / 2 + 245]
        for i, name in enumerate(COMPANIES):
            col = i % 2; row = i // 2
            x = cols[col]; y = 780 + row * 150
            st = T_UP + 0.35 + i * 0.17
            p = eo((t - st) / 0.45)
            if p <= 0: continue
            # connector
            d = ImageDraw.Draw(c)
            lx = lerp(W / 2, x, p); ly = lerp(625, y - 55, p)
            d.line((W / 2, 625, lx, ly), fill=ACCENT + (int(150 * a_all),), width=3)
            tile = rrect(440, 112, 22, (16, 19, 52, 225), ACCENT + (200,), 2)
            put(c, tile, x, y + (1 - p) * 40, a_all * p)
            put(c, fit(name, 'Bold', 390, 34), x, y + (1 - p) * 40, a_all * p)
        reveal(c, text_img('DÉCADAS DE ATUAÇÃO', 'Medium', 38, tracking=8), W / 2, 1400, t, 25.0, 27.0, a=a_all)
        reveal(c, text_img('EM DIFERENTES SETORES DA ECONOMIA', 'Medium', 34, SOFT, tracking=4), W / 2, 1400, t, 27.3, 28.85)

def counter_str(v, kind):
    if kind == 'year': return f'{int(v)}'
    if kind == 'plus': return '+' + f'{int(v):,}'.replace(',', '.')
    return str(int(v))

def card_classic(c, t, sp):
    t0, t1 = sp['t0'], sp['t1']
    if not (t0 <= t < t1 + 0.4): return
    tx = t1 - 0.32
    idx = sp['idx']
    reveal(c, text_img(f'IDEA HOLDING  ·  0{idx + 1}/08', 'Medium', 32, SOFT, tracking=6), W / 2, 420, t, t0 + 0.1, tx)
    if t > t0 + 0.25:
        ln = eo((t - t0 - 0.25) / 0.5) * 120 * (1 - ei((t - tx) / 0.3))
        hbar(c, W / 2, 470, ln, 5, ACCENT, anchor='c')
    y = 560
    for k, line in enumerate(sp['name']):
        im = fit(line, 'Black', 960, sp.get('name_size', 132))
        reveal(c, im, W / 2, y + im.height / 2 - PAD, t, sp['t_name'] + k * 0.12, tx)
        y += im.height - 2 * PAD + 6
    y += 40
    for k, (line, tl) in enumerate(sp.get('desc', [])):
        im = text_img(line, 'SemiBold', 46, (232, 235, 255))
        reveal(c, im, W / 2, y + 30, t, tl, tx)
        y += 64
    if sp.get('stat'):
        st = sp['stat']
        y += 40
        if st.get('label_top'):
            reveal(c, text_img(st['label_top'], 'Medium', 40, SOFT, tracking=6), W / 2, y + 25, t, st['t_label_top'], tx)
            y += 70
        if t >= st['t']:
            p = eo((t - st['t']) / st.get('dur', 1.1))
            v = lerp(st['from'], st['to'], p)
            im = text_img(counter_str(v, st['kind']), 'Black', 210, WHITE)
            reveal(c, im, W / 2, y + 110, t, st['t'], tx, dur=0.4)
        y += 230
        for k, (line, tl) in enumerate(st.get('label', [])):
            reveal(c, text_img(line, 'Medium', 40, SOFT, tracking=2), W / 2, y + 22, t, tl, tx)
            y += 56
    for k, (tag, tl) in enumerate(sp.get('tags', [])):
        p = pill(tag, 34, tracking=6, fill=(18, 22, 60, 230), outline=ACCENT + (255,))
        pop(c, p, W / 2, sp.get('tag_y', 1180) + k * 96, t, tl, tx, s0=1.3)
    a = fade_in_out(t, t0 + 0.2, tx)
    dots(c, 1500, idx, a)

def card_tech(c, t, sp):
    t0, t1 = sp['t0'], sp['t1']
    if not (t0 <= t < t1 + 0.4): return
    tx = t1 - 0.28
    idx = sp['idx']
    a = fade_in_out(t, t0, tx, 0.3, 0.28)
    # giant index
    big = text_img(f'0{idx + 1}', 'Black', 560, ACCENT, shadow=0)
    put(c, big, W / 2 + (1 - eo((t - t0) / 0.8)) * 120, 470, a * 0.16)
    reveal(c, text_img(f'NOVA GERAÇÃO  ·  0{idx + 1}/08', 'Medium', 32, SOFT, tracking=6), W / 2, 700, t, t0 + 0.08, tx)
    # name with glitch-in
    y = 800
    for k, line in enumerate(sp['name']):
        im = fit(line, 'Black', 960, sp.get('name_size', 140))
        cy = y + im.height / 2 - PAD
        tn = sp['t_name'] + k * 0.1
        if t >= tn:
            g = t - tn
            al = a * clamp(g / 0.15)
            if g < 0.28:
                j = int(18 * (1 - g / 0.28)) * (1 if int(g * 60) % 2 else -1)
                put(c, tint_img(im, (255, 60, 90)), W / 2 + j, cy, 0.55 * al)
                put(c, tint_img(im, (60, 200, 255)), W / 2 - j, cy, 0.55 * al)
            put(c, im, W / 2, cy, al)
            # scan line
            if g < 0.6:
                sy = cy - im.height / 2 + eio(g / 0.6) * im.height
                hbar(c, W / 2, sy, 1000, 3, (180, 195, 255), a * (1 - g / 0.6), anchor='c')
        y += im.height - 2 * PAD + 4
    # typewriter descriptor
    y += 46
    desc, td = sp['desc'], sp['t_desc']
    if t >= td:
        n = int(clamp((t - td) / sp.get('type_dur', 1.2)) * len(desc))
        lines = sp.get('desc_lines') or [desc]
        shown = 0
        for line in lines:
            k = clamp(n - shown, 0, len(line)); shown += len(line) + 1
            if k <= 0: break
            im = text_img(line[:k], 'SemiBold', 50, (232, 235, 255))
            fullw = text_img(line, 'SemiBold', 50).width
            x0 = W / 2 - fullw / 2
            c.alpha_composite(alpha_img(im, a), (int(x0), int(y)))
            if k < len(line) or (line is lines[-1] and int(t * 3) % 2 == 0):
                cx = x0 + im.width - PAD + 6
                hbar(c, cx, y + im.height / 2, 5, 52, ACCENT, a)
            y += 70
    dots(c, 1500, idx, a)

def tint_img(im, color):
    out = Image.new('RGBA', im.size, color + (0,))
    out.putalpha(im.getchannel('A'))
    return out

CARDS_S3 = [
    dict(idx=0, t0=29.2, t1=37.85, name=['Arthur D. Little'], t_name=30.15,
         stat=dict(label_top='FUNDADA NO BRASIL EM', t_label_top=31.35, t=32.55, **{'from': 1950, 'to': 1972}, kind='year', dur=1.0),
         tags=[('GESTÃO ESTRATÉGICA', 35.45), ('CONSULTORIA', 36.8)], tag_y=1230),
    dict(idx=1, t0=37.85, t1=47.05, name=['Magna Capital'], t_name=38.4,
         desc=[('Gestão de ativos e', 40.3), ('viabilidade financeira', 41.5)],
         stat=dict(t=43.82, **{'from': 0, 'to': 1000}, kind='plus', dur=1.1,
                   label=[('projetos de viabilidade', 44.15), ('financeira realizados', 45.6)])),
    dict(idx=2, t0=47.05, t1=56.95, name=['ITEC'], t_name=47.38, name_size=170,
         desc=[('Engenharia de infraestrutura', 48.85), ('e gerenciamento de execução', 50.7)],
         stat=dict(t=53.78, **{'from': 0, 'to': 550}, kind='plus', dur=1.0,
                   label=[('projetos de', 54.95), ('infraestrutura', 55.55)])),
]
CARDS_S4 = [
    dict(idx=3, t0=61.85, t1=67.20, name=['IDEA Corporate', 'Minority Holdings'], t_name=62.15, name_size=110,
         desc='Participações em negócios estratégicos', desc_lines=['Participações em', 'negócios estratégicos'], t_desc=64.4, type_dur=1.6),
    dict(idx=4, t0=67.20, t1=71.45, name=['Nia'], t_name=67.48, name_size=230,
         desc='Desenvolvimento tecnológico e aplicações', desc_lines=['Desenvolvimento tecnológico', 'e aplicações'], t_desc=68.5, type_dur=1.8),
    dict(idx=5, t0=71.45, t1=75.95, name=['Oasis Cloud'], t_name=71.68,
         desc='Tecnologia e armazenamento digital', desc_lines=['Tecnologia e', 'armazenamento digital'], t_desc=73.3, type_dur=1.6),
    dict(idx=6, t0=75.95, t1=80.70, name=['VennTure', 'Capital'], t_name=76.24,
         desc='Finanças e boutique de investimentos', desc_lines=['Finanças e boutique', 'de investimentos'], t_desc=78.2, type_dur=1.6),
    dict(idx=7, t0=80.70, t1=84.60, name=['Engemega'], t_name=81.05,
         desc='Construção civil', desc_lines=['Construção civil'], t_desc=82.9, type_dur=0.8),
]

def ov_s4_intro(c, t):
    if not (56.95 <= t < 62.1): return
    tx = 61.55
    reveal(c, text_img('NOVA GERAÇÃO DE NEGÓCIOS', 'Medium', 38, SOFT, tracking=10), W / 2, 640, t, 57.05, tx)
    if t > 57.3:
        ln = eo((t - 57.3) / 0.6) * 140 * (1 - ei((t - tx) / 0.3))
        hbar(c, W / 2, 695, ln, 5, ACCENT, anchor='c')
    reveal(c, fit('A EVOLUÇÃO', 'Black', 960, 120), W / 2, 800, t, 58.7, tx)
    reveal(c, fit('DO MERCADO', 'Black', 960, 120), W / 2, 930, t, 59.4, tx)
    reveal(c, text_img('E DAS NOVAS', 'Light', 62, tracking=12), W / 2, 1050, t, 60.05, tx)
    reveal(c, fit('TECNOLOGIAS', 'Black', 960, 120, color=SOFT), W / 2, 1165, t, 60.7, tx)

WORDS_S5 = [(84.69, 'EXPERIÊNCIA'), (85.62, 'INOVAÇÃO'), (86.9, 'CAPITAL'), (87.54, 'TECNOLOGIA'),
            (88.82, 'INFRAESTRUTURA'), (89.94, 'EMPREENDEDORISMO')]

def ov_s5(c, t):
    if 84.6 <= t < 91.2:
        for k, (tw, wd) in enumerate(WORDS_S5):
            nxt = WORDS_S5[k + 1][0] if k + 1 < len(WORDS_S5) else 90.85
            if tw <= t < nxt + 0.2:
                pop(c, fit(wd, 'Black', 980, 150), W / 2, 960, t, tw, nxt - 0.12, dur=0.3, s0=1.25, out_dur=0.12)
            # accumulated list
            if t >= nxt - 0.05 and k < len(WORDS_S5) - 1 or (k == len(WORDS_S5) - 1 and t >= 90.5):
                a = fade_in_out(t, nxt - 0.05, 90.75, 0.25, 0.3)
                put(c, text_img(wd, 'SemiBold', 34, SOFT, tracking=8), W / 2, 1150 + k * 52, a * 0.85)
    if 90.95 <= t < 99.9:
        reveal(c, text_img('QUANDO HISTÓRIAS', 'Black', 76), W / 2, 1100, t, 91.3, 93.25)
        reveal(c, text_img('COMO ESSA SE ENCONTRAM', 'Light', 52, tracking=4), W / 2, 1195, t, 92.0, 93.3)
        reveal(c, text_img('COM UMA COMUNIDADE', 'Black', 76), W / 2, 1070, t, 93.5, 97.2)
        reveal(c, text_img('DE EMPRESÁRIOS QUE', 'Light', 52, tracking=4), W / 2, 1165, t, 94.4, 97.25)
        reveal(c, text_img('TAMBÉM PENSAM', 'Light', 52, tracking=4), W / 2, 1235, t, 95.75, 97.3)
        pop(c, text_img('GRANDE', 'Black', 230, SOFT), W / 2, 1390, t, 96.6, 97.3, s0=1.6)
        reveal(c, fit('NOVAS POSSIBILIDADES', 'Black', 960, 96), W / 2, 1150, t, 97.45, 99.3)
        reveal(c, text_img('SURGEM.', 'Light', 64, SOFT, tracking=20), W / 2, 1265, t, 98.8, 99.35)

def ov_s6(c, t):
    if 99.6 <= t < 104.0:
        reveal(c, text_img('E SE HOJE', 'Light', 64, tracking=14), W / 2, 820, t, 99.7, 103.4)
        reveal(c, fit('ESTAMOS MOSTRANDO', 'Black', 960, 108), W / 2, 930, t, 100.2, 103.45)
        reveal(c, fit('APENAS O ENCONTRO…', 'Black', 960, 108, color=SOFT), W / 2, 1050, t, 101.3, 103.5)
    if 103.65 <= t < 108.3:
        reveal(c, text_img('…É PORQUE AINDA', 'Light', 60, tracking=10), W / 2, 780, t, 103.7, 107.6)
        reveal(c, fit('NÃO PODEMOS MOSTRAR', 'Black', 980, 104), W / 2, 885, t, 104.45, 107.6)
        reveal(c, fit('TUDO O QUE ESTÁ', 'Black', 980, 104), W / 2, 1000, t, 105.8, 107.65)
        reveal(c, fit('SENDO CONSTRUÍDO.', 'Black', 980, 104, color=SOFT), W / 2, 1115, t, 106.55, 107.7)

PORTRAITS = [('7768', 2.0, 600, 640, 600, 'DAHER', 'PRESIDENTE'),
             ('7772', 1.0, 520, 800, 560, 'CLÁUDIA', 'VICE-PRESIDENTE'),
             ('7769', 2.0, 510, 760, 640, 'PEDRO', 'SÓCIO')]
PSZ = 168

@functools.lru_cache(1)
def portrait_imgs():
    out = []
    for clip, ts, cx, cy, sz, name, role in PORTRAITS:
        raw = subprocess.run(['ffmpeg', '-v', 'error', '-ss', str(ts), '-i', os.path.join(S, 'src', clip + '.mp4'),
                              '-frames:v', '1', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-'], capture_output=True).stdout
        im = Image.frombuffer('RGB', (W, H), raw, 'raw', 'RGB', 0, 1)
        im = im.crop((cx - sz // 2, cy - sz // 2, cx + sz // 2, cy + sz // 2)).resize((PSZ, PSZ), Image.LANCZOS)
        m = Image.new('L', (PSZ * 4, PSZ * 4), 0); ImageDraw.Draw(m).ellipse((0, 0, PSZ * 4 - 1, PSZ * 4 - 1), fill=255)
        m = m.resize((PSZ, PSZ), Image.LANCZOS)
        ring = Image.new('RGBA', (PSZ + 14, PSZ + 14), (0, 0, 0, 0))
        ImageDraw.Draw(ring).ellipse((0, 0, PSZ + 13, PSZ + 13), fill=ACCENT + (255,))
        im = im.convert('RGBA'); im.putalpha(m)
        ring.alpha_composite(im, (7, 7))
        out.append((ring, text_img(name, 'Bold', 28, tracking=2), text_img(role, 'Medium', 19, SOFT, tracking=1)))
    return out

def name_tag(c, t, t0, t1, name, role):
    if t < t0 or t > t1 + 0.4: return
    reveal(c, text_img(name, 'Black', 64), W / 2, 300, t, t0, t1)
    reveal(c, pill(role, 30, tracking=6), W / 2, 385, t, t0 + 0.15, t1)

def ov_final(c, t):
    if t < 108.1: return
    tl = t - 108.1
    # flash
    if tl < 0.5:
        fl = Image.new('RGBA', (W, H), (235, 238, 255, int(255 * (1 - eo(tl / 0.5)))))
        c.alpha_composite(fl)
    # rings
    for k in range(3):
        rp = ((tl - 0.1 - k * 0.9) % 2.7) / 2.7 if tl > 0.1 + k * 0.9 else None
        if rp is None: continue
        sz = int(lerp(380, 1250, eo(rp)))
        put(c, RING.resize((sz, sz), Image.BILINEAR), W / 2, 640, (1 - rp) * 0.5)
    lg = eback(tl / 0.7)
    sz = int(400 * max(0.05, lg))
    put(c, glow_disc(700), W / 2, 640, clamp(tl / 0.6) * 0.8)
    put(c, logo_sized(max(8, sz)), W / 2, 640, clamp(tl / 0.25))
    reveal(c, text_img('UMA GRANDE CONEXÃO', 'Black', 80), W / 2, 960, t, 108.3, 111.0)
    reveal(c, text_img('ACABA DE COMEÇAR.', 'Light', 62, SOFT, tracking=8), W / 2, 1050, t, 109.25, 111.05)
    reveal(c, text_img('E VEM ALGO', 'Light', 62, tracking=8), W / 2, 950, t, 111.3, 113.55)
    reveal(c, fit('GRANDIOSO POR AÍ', 'Black', 960, 104, color=SOFT), W / 2, 1050, t, 111.95, 113.6)
    if t >= 113.75:
        reveal(c, fit('LÍDERES DO BRASIL', 'Black', 960, 104), W / 2, 950, t, 113.8)
        if t >= 114.6:
            pop(c, pill('EM BREVE', 46, tracking=14, padx=48, pady=22), W / 2, 1110, t, 114.6, s0=1.5)
    # end fade
    if t > DUR - 0.6:
        c.alpha_composite(Image.new('RGBA', (W, H), (0, 0, 0, int(255 * clamp((t - (DUR - 0.6)) / 0.6)))))


def overlays(c, T):
    ov_s1(c, T)
    ov_s2(c, T)
    ov_s3_intro(c, T)
    for sp in CARDS_S3: card_classic(c, T, sp)
    ov_s4_intro(c, T)
    for sp in CARDS_S4: card_tech(c, T, sp)
    ov_s5(c, T)
    ov_s6(c, T)
    ov_final(c, T)
    # cut flashes at section starts
    for st in SECTION_STARTS[1:6]:
        if st <= T < st + 0.22:
            a = 1 - eo((T - st) / 0.22)
            c.alpha_composite(Image.new('RGBA', (W, H), (230, 234, 255, int(150 * a))))


# ----------------------------------------------------------------- main
def render_range(f0, f1, out_path):
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}',
                            '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '17',
                            '-pix_fmt', 'yuv420p', '-profile:v', 'high', out_path], stdin=subprocess.PIPE)
    bg = BG()
    for f in range(f0, f1):
        T = f / FPS
        c, s, tau = bg.frame(T)
        overlays(c, T)
        enc.stdin.write(c.convert('RGB').tobytes())
        if f % 150 == 0: print(f'{out_path}: {T:.1f}s', flush=True)
    enc.stdin.close(); enc.wait()
    for r in bg.readers: r.close()


def chunks(n):
    total = int(round(DUR * FPS))
    cuts = [int(round(s['t0'] * FPS)) for s in SEGS] + [total]
    bounds = [0]
    for k in range(1, n):
        target = total * k / n
        bounds.append(min(cuts, key=lambda x: abs(x - target)))
    bounds.append(total)
    return sorted(set(bounds))


if __name__ == '__main__':
    os.makedirs(os.path.join(S, 'out'), exist_ok=True)
    if sys.argv[1] == 'still':
        for ts in sys.argv[2:]:
            T = float(ts); bg = BG(); c, s, tau = bg.frame(T); overlays(c, T)
            c.convert('RGB').save(os.path.join(S, 'out', f'still_{T:06.2f}.jpg'), quality=88)
            for r in bg.readers: r.close()
    else:
        k, n = int(sys.argv[1]), int(sys.argv[2])
        b = chunks(n)
        render_range(b[k], b[k + 1], os.path.join(S, 'out', f'chunk_{k:02d}.mp4'))
