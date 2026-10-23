"""30s Stories cut of LÍDERES DO BRASIL × ADRIANO AMARAL, built from the full version's pieces.

usage: python3 story.py <chunk_index> <n_chunks>  -> out/story_XX.mp4
       python3 story.py still <t> [t ...]
"""
import os, sys, subprocess
from PIL import Image, ImageDraw
import render as R
from render import (W, H, FPS, L, reveal, pop, put, fit, text_img, pill, hbar, eo, ei, eback, clamp, lerp,
                    logo_sized, glow_disc, RING, ACCENT, SOFT, WHITE)

DUR = 36.75
IDEA_AT = 11.15          # story time where the IDEA Holding narration line starts
SH_S6 = 76.0             # full-edit time = story time + SH_S6 during the climax
IMPACT = 108.12 - SH_S6  # 32.12
# word onsets inside idea.mp3 (seconds)
NAME_T = [3.08, 4.21, 5.40, 6.06, 8.34, 8.99, 10.18, 11.40]

SEGS = [s for s in R.SEGS if s['t1'] <= 8.2 + 1e-6] + [
    dict(t0=8.20, t1=11.05, split=(L('7772_2', 1.6, 0.6, (1.0, 1.08)), L('7771', 5.0, 0.6, (1.0, 1.08))),
         fy=(900, 790), dim=0.8),
]
SEGS += [
    dict(t0=11.05, t1=13.80, l=L('7774', 2.8, 0.55, (1.05, 1.25)), dim=0.42, blur=4),
    dict(t0=13.80, t1=16.20, l=L('7772', 5.0, 0.8, (1.1, 1.2)), dim=0.36, blur=12, grid=True, tint=True),
    dict(t0=16.20, t1=18.90, l=L('7768', 0.0, 1.0, (1.1, 1.2)), dim=0.36, blur=12, grid=True, tint=True),
    dict(t0=18.90, t1=21.20, l=L('7771', 0.0, 1.0, (1.1, 1.2)), dim=0.36, blur=12, grid=True, tint=True),
    dict(t0=21.20, t1=99.6 - SH_S6, l=L('7769', 3.0, 1.0, (1.1, 1.2)), dim=0.36, blur=12, grid=True, tint=True),
]
for s in R.SEGS:
    if 99.6 <= s['t0'] < 108.1:
        d = dict(s); d['t0'] = s['t0'] - SH_S6; d['t1'] = s['t1'] - SH_S6
        SEGS.append(d)
SEGS.append(dict(t0=108.1 - SH_S6, t1=DUR + 0.01, final=True))
CUTS = [s['t0'] for s in SEGS]

R.SEGS = SEGS
R.DUR = DUR


def ov_idea(c, t):
    if t < 13.8:
        reveal(c, text_img('POR TRÁS DESSA HISTÓRIA', 'Medium', 38, SOFT, tracking=10), W / 2, 700, t, 11.2, 13.55)
        reveal(c, text_img('IDEA', 'Black', 230), W / 2, 860, t, 12.55, 13.6)
        reveal(c, text_img('HOLDING', 'Light', 70, tracking=40), W / 2, 1010, t, 12.85, 13.6)
        return
    a_all = 1 - clamp((t - (99.6 - SH_S6 - 0.35)) / 0.3)
    reveal(c, text_img('IDEA HOLDING', 'Black', 92), W / 2, 330, t, 13.8, 99.6 - SH_S6 - 0.35)
    hub = eo((t - 13.9) / 0.4)
    put(c, R.glow_disc(160), W / 2, 470, a_all * hub)
    put(c, R.rrect(22, 22, 11, ACCENT + (255,)), W / 2, 470, a_all * hub)
    cols = [W / 2 - 245, W / 2 + 245]
    cur = -1
    for i, name in enumerate(R.COMPANIES):
        st = IDEA_AT + NAME_T[i] - 0.05
        if t >= st: cur = i
    d = ImageDraw.Draw(c)
    for i, name in enumerate(R.COMPANIES):
        st = IDEA_AT + NAME_T[i] - 0.05
        p = eo((t - st) / 0.4)
        if p <= 0: continue
        x = cols[i % 2]; y = 620 + (i // 2) * 150
        lx = lerp(W / 2, x, p); ly = lerp(470, y - 55, p)
        d.line((W / 2, 470, lx, ly), fill=ACCENT + (int(150 * a_all),), width=3)
    for i, name in enumerate(R.COMPANIES):
        st = IDEA_AT + NAME_T[i] - 0.05
        p = eo((t - st) / 0.4)
        if p <= 0: continue
        x = cols[i % 2]; y = 620 + (i // 2) * 150
        on = i == cur
        tile = R.rrect(440, 112, 22, (ACCENT + (240,)) if on else (16, 19, 52, 225), ACCENT + (220,), 2)
        put(c, tile, x, y + (1 - p) * 40, a_all * p)
        put(c, fit(name, 'Bold', 390, 34), x, y + (1 - p) * 40, a_all * p)
    if cur >= 0:
        st = IDEA_AT + NAME_T[cur] - 0.05
        nxt = IDEA_AT + NAME_T[cur + 1] - 0.05 if cur + 1 < 8 else 99.6 - SH_S6 - 0.35
        lines = {3: ['IDEA Corporate', 'Minority Holdings'], 6: ['VennTure Capital']}.get(cur, [R.COMPANIES[cur]])
        for k, ln in enumerate(lines):
            im = fit(ln, 'Black', 960, 110 if len(lines) > 1 else 124, color=WHITE)
            yy = 1300 + (k - (len(lines) - 1) / 2) * 112
            pop(c, im, W / 2, yy, t, st, nxt - 0.1, dur=0.3, s0=1.2, out_dur=0.1)


def ov_story_final(c, t):
    if t < IMPACT - 0.02: return
    tl = t - (IMPACT - 0.02)
    if tl < 0.5:
        c.alpha_composite(Image.new('RGBA', (W, H), (235, 238, 255, int(255 * (1 - eo(tl / 0.5))))))
    for k in range(3):
        if tl <= 0.1 + k * 0.9: continue
        rp = ((tl - 0.1 - k * 0.9) % 2.7) / 2.7
        sz = int(lerp(380, 1250, eo(rp)))
        put(c, RING.resize((sz, sz), Image.BILINEAR), W / 2, 640, (1 - rp) * 0.5)
    sz = int(400 * max(0.05, eback(tl / 0.7)))
    put(c, glow_disc(700), W / 2, 640, clamp(tl / 0.6) * 0.8)
    put(c, logo_sized(max(8, sz)), W / 2, 640, clamp(tl / 0.25))
    E = IMPACT + 0.23
    reveal(c, text_img('E VEM ALGO', 'Light', 62, tracking=8), W / 2, 950, t, E, E + 2.15)
    reveal(c, fit('GRANDIOSO POR AÍ', 'Black', 960, 104, color=SOFT), W / 2, 1050, t, E + 0.55, E + 2.2)
    if t >= E + 2.35:
        reveal(c, fit('LÍDERES DO BRASIL', 'Black', 960, 104), W / 2, 950, t, E + 2.4)
        pop(c, pill('EM BREVE', 46, tracking=14, padx=48, pady=22), W / 2, 1110, t, E + 2.85, s0=1.5)
    if t > DUR - 0.5:
        c.alpha_composite(Image.new('RGBA', (W, H), (0, 0, 0, int(255 * clamp((t - (DUR - 0.5)) / 0.5)))))


def overlays(c, t):
    if t < 8.2:
        R.ov_s1(c, t)
    elif t < 11.05:
        a0 = 8.35
        band = eo((t - a0) / 0.5) * W * (1 - ei((t - 10.8) / 0.25))
        hbar(c, W / 2, H / 2, band, 150, (12, 14, 40), 0.82, anchor='c')
        hbar(c, W / 2, H / 2 - 75, band, 4, ACCENT, anchor='c')
        hbar(c, W / 2, H / 2 + 75, band, 4, ACCENT, anchor='c')
        reveal(c, fit('DUAS GERAÇÕES', 'Black', 900, 92), W / 2, H / 2, t, 8.6, 10.75, dur=0.4, out_dur=0.25)
    elif t < 99.6 - SH_S6:
        ov_idea(c, t)
    elif t < IMPACT:
        R.ov_s6(c, t + SH_S6)
    ov_story_final(c, t)
    for st in (11.05, 13.8, 99.6 - SH_S6):
        if st <= t < st + 0.22:
            a = 1 - eo((t - st) / 0.22)
            c.alpha_composite(Image.new('RGBA', (W, H), (230, 234, 255, int(150 * a))))


def render_range(f0, f1, out_path):
    enc = subprocess.Popen(['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-s', f'{W}x{H}',
                            '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'medium', '-crf', '17',
                            '-pix_fmt', 'yuv420p', '-profile:v', 'high', out_path], stdin=subprocess.PIPE)
    bg = R.BG()
    for f in range(f0, f1):
        T = f / FPS
        c, s, tau = bg.frame(T)
        overlays(c, T)
        enc.stdin.write(c.convert('RGB').tobytes())
    enc.stdin.close(); enc.wait()
    for r in bg.readers: r.close()


if __name__ == '__main__':
    out = os.path.join(R.S, 'out')
    if sys.argv[1] == 'still':
        for ts in sys.argv[2:]:
            T = float(ts); bg = R.BG(); c, s, tau = bg.frame(T); overlays(c, T)
            c.convert('RGB').save(os.path.join(out, f'story_{T:05.2f}.jpg'), quality=88)
            for r in bg.readers: r.close()
    elif sys.argv[1] == 'cuts':
        print(' '.join(f'{x:.2f}' for x in CUTS))
    else:
        k, n = int(sys.argv[1]), int(sys.argv[2])
        total = int(round(DUR * FPS))
        cuts = [int(round(x * FPS)) for x in CUTS] + [total]
        bounds = [0] + [min(cuts, key=lambda x: abs(x - total * i / n)) for i in range(1, n)] + [total]
        bounds = sorted(set(bounds))
        render_range(bounds[k], bounds[k + 1], os.path.join(out, f'story_{k:02d}.mp4'))
