"""30s Stories cut of LÍDERES DO BRASIL × ADRIANO AMARAL, built from the full version's pieces.

usage: python3 story.py <chunk_index> <n_chunks>  -> out/story_XX.mp4
       python3 story.py still <t> [t ...]
"""
import os, sys, subprocess
from PIL import Image
import render as R
from render import (W, H, FPS, L, reveal, pop, put, fit, text_img, pill, hbar, eo, ei, eback, clamp, lerp,
                    logo_sized, glow_disc, RING, ACCENT, SOFT)

DUR = 31.0
SH_S5 = 84.6 - 11.05     # full-edit time = story time + SH_S5 during the values section
SH_S6 = 81.75            # full-edit time = story time + SH_S6 during the climax
IMPACT = 108.12 - SH_S6  # 26.37

SEGS = [s for s in R.SEGS if s['t1'] <= 8.2 + 1e-6] + [
    dict(t0=8.20, t1=11.05, split=(L('7772_2', 1.6, 0.6, (1.0, 1.08)), L('7771', 5.0, 0.6, (1.0, 1.08))),
         fy=(900, 790), dim=0.8),
]
for s in R.SEGS:
    if 84.6 <= s['t0'] < 90.95:
        d = dict(s); d['t0'] = s['t0'] - SH_S5; d['t1'] = s['t1'] - SH_S5
        SEGS.append(d)
SEGS[-1]['t1'] = 99.6 - SH_S6
for s in R.SEGS:
    if 99.6 <= s['t0'] < 108.1:
        d = dict(s); d['t0'] = s['t0'] - SH_S6; d['t1'] = s['t1'] - SH_S6
        SEGS.append(d)
SEGS.append(dict(t0=108.1 - SH_S6, t1=DUR + 0.01, final=True))
CUTS = [s['t0'] for s in SEGS]

R.SEGS = SEGS
R.DUR = DUR


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
    reveal(c, text_img('E VEM ALGO', 'Light', 62, tracking=8), W / 2, 950, t, 26.6, 28.75)
    reveal(c, fit('GRANDIOSO POR AÍ', 'Black', 960, 104, color=SOFT), W / 2, 1050, t, 27.15, 28.8)
    if t >= 28.95:
        reveal(c, fit('LÍDERES DO BRASIL', 'Black', 960, 104), W / 2, 950, t, 29.0)
        pop(c, pill('EM BREVE', 46, tracking=14, padx=48, pady=22), W / 2, 1110, t, 29.45, s0=1.5)
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
        R.ov_s5(c, min(t + SH_S5, 90.9))
    elif t < IMPACT:
        R.ov_s6(c, t + SH_S6)
    ov_story_final(c, t)
    for st in (11.05, 99.6 - SH_S6):
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
