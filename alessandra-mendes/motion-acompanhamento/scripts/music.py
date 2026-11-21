"""Trilha sintetizada (pad quente + plucks + batida leve) para o motion da Alê. -> ../audio/music.wav"""
import numpy as np, wave, os
SR = 44100; DUR = 57.5; BPM = 84; BEAT = 60 / BPM
VO = 0.4
n = int(SR * DUR); L = np.zeros(n); R = np.zeros(n)
def midi(m): return 440 * 2 ** ((m - 69) / 12)
def lp(x, a):
    y = np.zeros_like(x); acc = 0.0
    for i in range(len(x)): acc += a * (x[i] - acc); y[i] = acc
    return y
def add(buf, t0, sig, g=1.0):
    i = int(t0 * SR); j = min(len(buf), i + len(sig))
    if i < len(buf): buf[i:j] += sig[:j - i] * g
# acordes: Fmaj7 · Am7 · Dm7 · Bbmaj7 (2 compassos cada)
CH = [[53, 57, 60, 64], [57, 60, 64, 67], [50, 53, 57, 60], [46, 50, 53, 57]]
bar = BEAT * 4
t = np.arange(int(SR * bar * 2)) / SR
for k in range(int(DUR / (bar * 2)) + 1):
    notes = CH[k % 4]; seg = np.zeros_like(t)
    for m in notes:
        f = midi(m)
        seg += sum(np.sin(2 * np.pi * f * (1 + d) * t + ph) for d, ph in ((-.003, 0), (.003, 1.3), (0, 2.1))) / 3
    env = np.minimum(1, t / 1.2) * np.minimum(1, (t[-1] - t) / 1.0)
    pad = lp(seg * env, 0.08) * 0.11
    add(L, k * bar * 2, pad); add(R, k * bar * 2, pad * .92)
# plucks (arpejo) a partir de 'Aqui comigo' (19.7 s de narração)
def pluck(f, d=0.6):
    tt = np.arange(int(SR * d)) / SR
    return (np.sin(2 * np.pi * f * tt) + .35 * np.sin(4 * np.pi * f * tt) + .12 * np.sin(6 * np.pi * f * tt)) * np.exp(-tt * 6)
start = 19.7 + VO; step = BEAT / 2; i = 0; tt = start
while tt < DUR - 4:
    k = int(tt / (bar * 2)) % 4; m = CH[k][i % 4] + 12
    add(L if i % 2 else R, tt, pluck(midi(m)), .05); i += 1; tt += step
# batida suave
def kick():
    tt = np.arange(int(SR * .35)) / SR; f = 50 + 70 * np.exp(-tt * 30)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-tt * 9)
def hat():
    tt = np.arange(int(SR * .06)) / SR; return np.random.default_rng(1).standard_normal(len(tt)) * np.exp(-tt * 70)
tt = start
while tt < DUR - 3.5:
    add(L, tt, kick(), .22); add(R, tt, kick(), .22)
    add(L, tt + BEAT / 2, hat(), .018); add(R, tt + BEAT / 2, hat(), .022)
    tt += BEAT
# impacto suave em 'Aqui comigo' e no final
def swell(d=1.6):
    tt = np.arange(int(SR * d)) / SR
    noise = np.random.default_rng(2).standard_normal(len(tt))
    return lp(noise, 0.05) * (tt / d) ** 2
add(L, start - 1.6, swell(), .25); add(R, start - 1.6, swell(), .25)
add(L, 50.86 + VO - 1.6, swell(), .22); add(R, 50.86 + VO - 1.6, swell(), .22)
for b in (L, R):
    fade = np.ones(n); fo = int(SR * 2.5); fade[-fo:] = np.linspace(1, 0, fo); b *= fade
st = np.stack([L, R], 1); st /= np.max(np.abs(st)) / 0.8
os.makedirs(os.path.join(os.path.dirname(__file__), '..', 'audio'), exist_ok=True)
with wave.open(os.path.join(os.path.dirname(__file__), '..', 'audio', 'music.wav'), 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st * 32767).astype(np.int16).tobytes())
print('music ok')
