"""Synthesize a cinematic corporate music bed + riser + impact, synced to the edit timeline."""
import numpy as np, wave, sys

SR = 44100
OFF = 0.5                      # narration offset in the edit
DUR = 118.5
N = int(SR * DUR)
rng = np.random.default_rng(7)

BPM = 90.0
BEAT = 60.0 / BPM
BAR = BEAT * 4

# section boundaries (edit time)
S3 = 19.25 + OFF
S4 = 56.45 + OFF
S5 = 84.1 + OFF
S6 = 99.15 + OFF
IMPACT = 107.62 + OFF
END = DUR

def midi(n): return 440.0 * 2 ** ((n - 69) / 12)

# A minor: Am - F - C - G (vi IV I V of C)
CHORDS = [
    [57, 60, 64, 69],   # Am
    [53, 57, 60, 65],   # F
    [55, 60, 64, 67],   # C
    [55, 59, 62, 67],   # G
]
BASS = [45, 41, 48, 43]

t_all = np.arange(N) / SR
out = np.zeros(N)

def env_adsr(n, a, r, sr=SR):
    e = np.ones(n)
    na, nr = int(a * sr), int(r * sr)
    na = min(na, n); nr = min(nr, n)
    if na: e[:na] = np.linspace(0, 1, na)
    if nr: e[-nr:] *= np.linspace(1, 0, nr)
    return e

def lowpass(x, cutoff):
    # one-pole smoothing applied twice (12 dB/oct), vectorized via FFT filter for speed
    X = np.fft.rfft(x)
    f = np.fft.rfftfreq(len(x), 1 / SR)
    H = 1 / (1 + (f / cutoff) ** 4) ** 0.5
    return np.fft.irfft(X * H, len(x))

def saw(f, t, detune=0.0):
    ph = (f * (1 + detune)) * t
    return 2 * (ph - np.floor(ph + 0.5))

def add(buf, start, sig):
    i = int(start * SR)
    if i >= N: return
    j = min(N, i + len(sig))
    buf[i:j] += sig[: j - i]

# ---------- PAD ----------
pad = np.zeros(N)
bar_i = 0
t0 = 0.0
while t0 < END:
    ch = CHORDS[bar_i % 4]
    length = BAR + 1.2
    n = int(length * SR)
    t = np.arange(n) / SR
    s = np.zeros(n)
    for note in ch:
        f = midi(note)
        for d in (-0.004, 0.0, 0.0045):
            s += saw(f, t + rng.random(), d)
    s *= env_adsr(n, 0.9, 1.2)
    add(pad, t0, s)
    bar_i += 1
    t0 += BAR
pad = lowpass(pad, 1100) * 0.035
# pad volume automation
padvol = np.interp(t_all, [0, 1.5, S6 - 1, S6 + 0.5, IMPACT - 0.05, IMPACT, END - 4, END],
                          [0, 1.0, 1.0, 0.35, 0.35, 1.25, 1.1, 0])
out += pad * padvol

# ---------- SUB BASS ----------
bass = np.zeros(N)
bar_i = 0; t0 = 0.0
while t0 < END:
    f = midi(BASS[bar_i % 4])
    n = int((BAR + 0.1) * SR)
    t = np.arange(n) / SR
    s = np.sin(2 * np.pi * f * t) + 0.3 * np.sin(2 * np.pi * 2 * f * t)
    s *= env_adsr(n, 0.05, 0.3)
    add(bass, t0, s)
    bar_i += 1; t0 += BAR
bassvol = np.interp(t_all, [0, 6, S3, S6 - 0.5, S6, IMPACT, IMPACT + 0.01, END - 3, END],
                            [0, 0.08, 0.13, 0.15, 0.0, 0.0, 0.16, 0.12, 0])
out += bass * bassvol

# ---------- PLUCK ARP ----------
def pluck(f, dur=0.45):
    n = int(dur * SR); t = np.arange(n) / SR
    s = saw(f, t) * 0.6 + np.sin(2 * np.pi * f * t)
    s *= np.exp(-t * 7.5)
    s *= env_adsr(n, 0.003, 0.05)
    return s

arp = np.zeros(N)
pattern = [0, 2, 1, 3, 2, 1, 3, 2]
step = BEAT / 2
k = 0; t0 = S3 - BAR * 0  # start arp in S3
t0 = np.ceil(S3 / step) * step
while t0 < S6:
    bar_idx = int(t0 // BAR)
    ch = CHORDS[bar_idx % 4]
    note = ch[pattern[k % 8]] + 12
    add(arp, t0, pluck(midi(note)))
    k += 1
    t0 += step if t0 < S4 else step / 2   # 16ths in the tech section
arp = lowpass(arp, 3500) * 0.05
arpvol = np.interp(t_all, [S3, S3 + 3, S6 - 0.2, S6], [0, 1, 1, 0])
out += arp * arpvol

# ---------- DRUMS (S4..S6) ----------
drums = np.zeros(N)
def kick():
    n = int(0.45 * SR); t = np.arange(n) / SR
    f = 50 + 90 * np.exp(-t * 30)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return np.sin(ph) * np.exp(-t * 8)
def hat():
    n = int(0.06 * SR); t = np.arange(n) / SR
    s = rng.standard_normal(n); s = s - lowpass(s, 7000)
    return s * np.exp(-t * 70)
def clap():
    n = int(0.25 * SR); t = np.arange(n) / SR
    s = rng.standard_normal(n); s = lowpass(s, 4000) - lowpass(s, 900)
    return s * np.exp(-t * 18)
t0 = np.ceil(S4 / BEAT) * BEAT
b = 0
while t0 < S6 - 0.1:
    add(drums, t0, kick() * 0.55)
    add(drums, t0 + BEAT / 2, hat() * 0.12)
    if t0 > S5 and b % 2 == 1:
        add(drums, t0, clap() * 0.25)
    t0 += BEAT; b += 1
out += drums * 0.55

# ---------- PIANO-ish bell hits on chord changes (intro & outro) ----------
bell = np.zeros(N)
def bellnote(f, dur=3.0):
    n = int(dur * SR); t = np.arange(n) / SR
    s = np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * 2.01 * f * t) + 0.12 * np.sin(2 * np.pi * 3.0 * f * t)
    return s * np.exp(-t * 1.8) * env_adsr(n, 0.004, 0.2)
t0 = 0.0; bi = 0
while t0 < S3:
    ch = CHORDS[bi % 4]
    for j, nn in enumerate(ch[1:]):
        add(bell, t0 + j * 0.09, bellnote(midi(nn + 12)) * 0.5)
    bi += 1; t0 += BAR
for j, nn in enumerate([57, 64, 69, 72, 76]):
    add(bell, IMPACT + 0.05 + j * 0.12, bellnote(midi(nn + 12), 5.0) * 0.5)
out += bell * 0.05

# ---------- DRONE + RISER (S6) ----------
n = int((IMPACT - S6) * SR); t = np.arange(n) / SR
drone = (np.sin(2 * np.pi * midi(33) * t) + 0.5 * saw(midi(45), t)) * 0.1
drone = lowpass(drone, 400) * env_adsr(n, 1.0, 0.05)
add(out, S6, drone)
rs = IMPACT - 4.6
n = int((IMPACT - rs) * SR); t = np.arange(n) / SR
prog = t / t[-1]
noise = rng.standard_normal(n)
# sweep: progressively brighter noise built by crossfading lowpassed versions
lo = lowpass(noise, 600); mid = lowpass(noise, 3000); hi = noise
sweep = np.where(prog < 0.5, lo * (1 - prog * 2) + mid * prog * 2, mid * (2 - prog * 2) + hi * (prog * 2 - 1))
fr = 110 * 2 ** (prog * 3)
tone = saw(1, np.cumsum(fr) / SR) * 0.5
riser = (sweep * 0.11 + lowpass(tone, 2500) * 0.16) * prog ** 2.2
add(out, rs, riser)

# ---------- IMPACT ----------
n = int(4.5 * SR); t = np.arange(n) / SR
f = 35 + 70 * np.exp(-t * 6)
boom = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 1.3)
nz = lowpass(rng.standard_normal(n), 1500) * np.exp(-t * 4)
imp = boom * 0.55 + nz * 0.12
add(out, IMPACT, imp)

# ---------- small soft hits at section starts ----------
def softhit():
    n = int(1.5 * SR); t = np.arange(n) / SR
    f = 45 + 50 * np.exp(-t * 10)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 3) * 0.3
for st in (S3, S4, S5):
    add(out, st, softhit())

# ---------- REVERB (FFT convolution) ----------
irn = int(2.8 * SR); ti = np.arange(irn) / SR
ir = rng.standard_normal(irn) * np.exp(-ti * 2.4)
ir = lowpass(ir, 5000); ir /= np.sqrt((ir ** 2).sum())
L = 1 << int(np.ceil(np.log2(N + irn)))
wet = np.fft.irfft(np.fft.rfft(out, L) * np.fft.rfft(ir, L), L)[:N]
mix = out + wet * 0.35

# stereo widen with a tiny delay on the wet
right = out + np.roll(wet, int(0.013 * SR)) * 0.35
st = np.stack([mix, right], 1)
fade = np.interp(t_all, [0, 0.3, END - 3.5, END], [0, 1, 1, 0])
st *= fade[:, None]
st /= np.abs(st).max() / 0.89
pcm = (st * 32767).astype(np.int16)
with wave.open(sys.argv[1], 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes(pcm.tobytes())
print('ok', DUR)
