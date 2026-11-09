"""Musik + Soundeffekte für das Kuh-Dach-Video (ohne Sprecher).
Nutzung: python3 audio.py -> out/music_sfx.wav
"""
import json, os, wave
import numpy as np

SR = 48000
here = os.path.dirname(os.path.abspath(__file__))
DUR = json.load(open(os.path.join(here, "timeline.json")))["duration"]
N = int(DUR * SR)
rng = np.random.default_rng(13)
music = np.zeros(N); sfx = np.zeros(N)

LANDS = [5.7, 6.55, 7.15, 7.75, 11.2, 13.0, 14.8, 16.6, 18.4, 20.2, 22.0, 25.8]
CRASH, REW_A, REW_B = 31.2, 32.8, 33.5


def add(buf, t, sig, gain=1.0):
    i = int(t * SR)
    if i >= N or i < 0: return
    sig = sig[: N - i]; buf[i:i + len(sig)] += sig * gain


def ts(d): return np.arange(int(d * SR)) / SR
def noise(d): return rng.standard_normal(int(d * SR))
def hz(n): return 440 * 2 ** ((n - 69) / 12)


def env(n, a=0.005, r=None):
    t = np.arange(n) / SR; e = np.minimum(1, t / max(a, 1e-4))
    return e * np.exp(-t / r) if r else e


def tone(f, d, r=0.25, harm=(1, .5, .25), a=0.004):
    t = ts(d); s = sum(h * np.sin(2 * np.pi * f * (k + 1) * t) for k, h in enumerate(harm))
    return s * env(len(t), a, r)


def lowpass(x, a):
    y = np.empty_like(x); acc = 0.0
    for i, v in enumerate(x): acc += a * (v - acc); y[i] = acc
    return y


def reson(x, f, q):  # 2-Pol-Resonator (Formant)
    w = 2 * np.pi * f / SR; r = np.exp(-w / (2 * q))
    a1, a2 = -2 * r * np.cos(w), r * r
    y = np.zeros_like(x); y1 = y2 = 0.0
    for i, v in enumerate(x):
        yy = (1 - r) * v - a1 * y1 - a2 * y2; y[i] = yy; y2, y1 = y1, yy
    return y


def moo(d=1.1, base=110, bend=1.0):
    t = ts(d); n = len(t); k = t / d
    f0 = base * bend * (0.95 + 0.25 * np.sin(np.pi * k ** 0.7) - 0.15 * k) * (1 + 0.02 * np.sin(2 * np.pi * 5.5 * t))
    ph = np.cumsum(f0) / SR
    src = 2 * (ph % 1) - 1
    open_ = np.clip((k - 0.15) / 0.3, 0, 1)
    out = reson(src, 280, 4) * (1.2 - 0.5 * open_) + reson(src, 720, 6) * open_ + reson(src, 2400, 9) * 0.15 * open_
    e = np.clip(k / 0.08, 0, 1) * np.clip((1 - k) / 0.25, 0, 1)
    out = out * e
    return out / (np.max(np.abs(out)) + 1e-9)


def whistle(d=0.7, f1=1900, f2=500):
    t = ts(d); f = f1 * (f2 / f1) ** (t / d)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.clip(t / 0.05, 0, 1) * 0.8


def thump(d=0.45, f=55):
    t = ts(d)
    return np.sin(2 * np.pi * (f + 80 * np.exp(-t * 25)) * t) * np.exp(-t * 9) + lowpass(noise(d), 0.15) * np.exp(-t * 18) * 2


def popfx(f=520):
    t = ts(0.12); return np.sin(2 * np.pi * (f + 900 * np.exp(-t * 40)) * t) * np.exp(-t * 30)


# ---------- Musik: Polka (Umpa-Umpa), 140 BPM ----------
beat = 60 / 140
prog = [(60, [64, 67, 72]), (55, [62, 67, 71]), (60, [64, 67, 72]), (55, [62, 65, 71])]
melody = [72, 74, 76, 77, 79, 79, 77, 76, 74, 74, 76, 74, 72, 71, 72, 67]
t = 0.0; i = 0
while t < DUR:
    root, ch = prog[(i // 4) % 4]
    add(music, t, tone(hz(root - 24 + (7 if i % 2 else 0)), 0.35, 0.12, (1, .6, .3, .15)), 0.28)  # Tuba
    for n_ in ch: add(music, t + beat / 2, tone(hz(n_), 0.18, 0.06, (1, .5, .4, .3, .2)), 0.05)  # "pa"
    add(music, t, tone(hz(melody[i % 16]), beat * 0.9, 0.3, (1, .6, .45, .3, .2, .1), 0.01) * (1 + 0.15 * np.sin(2 * np.pi * 6 * ts(beat * 0.9))), 0.06)  # Akkordeon
    t += beat; i += 1
tt = np.arange(N) / SR
gate = np.clip(tt / 0.2, 0, 1) * np.clip((27.8 - tt) / 0.2, 0, 1) + np.clip((tt - 33.6) / 0.4, 0, 1) * 0.7
gate *= np.clip((DUR - tt) / 1.0, 0, 1)
music *= gate

# ---------- Kühe fallen ----------
for k, L in enumerate(LANDS):
    add(sfx, L - 0.7, whistle(0.7, 1900 + 60 * k, 520), 0.10)
    add(sfx, L, thump(), 0.55)
    add(sfx, L + 0.08, moo(1.0 + 0.2 * (k % 3), 95 + 9 * (k % 5)), 0.32)
    add(sfx, L + 0.05, tone(hz(72 + [0, 2, 4, 5, 7, 9, 11, 12, 14, 16, 17, 19][k]), 0.4, 0.15, (1, .2)), 0.12)  # Zähler-Ding
    if k >= 5:  # Dach knarzt
        d = 0.9; cr = lowpass(noise(d), 0.25) * (np.sin(2 * np.pi * (18 + 3 * k) * ts(d)) > 0.6)
        add(sfx, L + 0.3, cr * env(len(cr), 0.05, 0.4), 0.10 + 0.03 * (k - 5))
for c in [11.0, 15.4, 19.4, 23.9, 28.0, 34.6]:
    add(sfx, c, popfx(), 0.3)

# ---------- Spannung vor Kuh 13 ----------
d = CRASH - 27.8; t_ = ts(d); k_ = t_ / d
roll = noise(d) * (np.sin(2 * np.pi * 16 * t_) > 0) * (0.15 + 0.85 * k_)
add(sfx, 27.8, (roll - lowpass(roll, 0.3)) * 0.25)
siren = np.sin(2 * np.pi * np.cumsum(600 + 250 * np.sin(2 * np.pi * 1.6 * t_)) / SR) * k_
add(sfx, 27.8, siren, 0.06)
add(sfx, 28.1, moo(1.6, 70, 0.9), 0.5)  # tiefe Riesenkuh
add(sfx, 29.9, whistle(1.3, 1400, 160), 0.18)

# ---------- KRAWUMM ----------
t_ = ts(2.5)
boom = np.sin(2 * np.pi * (35 + 70 * np.exp(-t_ * 6)) * t_) * np.exp(-t_ * 2.2)
rubble = lowpass(noise(2.5), 0.08) * np.exp(-t_ * 1.6) * 3
add(sfx, CRASH, boom * 1.2 + rubble, 0.9)
add(sfx, CRASH, noise(0.2) * env(int(.2 * SR), 0.001, 0.05), 0.6)
for j in range(14):
    add(sfx, CRASH + 0.05 + rng.random() * 1.3, tone(600 + rng.random() * 1500, 0.2, 0.05, (1, .5)), 0.12)
for j, dt in enumerate([0.15, 0.35, 0.5, 0.7]):
    add(sfx, CRASH + dt, moo(0.8, 160 + 25 * j, 1.2), 0.22)

# ---------- Zurückspulen ----------
d = REW_B - REW_A; t_ = ts(d)
f = 300 + 2200 * (t_ / d) ** 2 + 150 * np.sin(2 * np.pi * 22 * t_)
add(sfx, REW_A, np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.6 + (noise(d) - lowpass(noise(d), 0.5)) * 0.15, 0.3)
add(sfx, REW_B, popfx(900), 0.4)

# ---------- Winter ----------
d = DUR - 33.6; wind = lowpass(noise(d), 0.006)
add(sfx, 33.6, wind * np.clip(ts(d) / 0.8, 0, 1) * np.clip((d - ts(d)) / 1.0, 0, 1), 3.0)
for j in range(22):
    add(sfx, 33.8 + rng.random() * 3.2, tone(hz(84 + rng.choice([0, 4, 7, 12])), 0.35, 0.08, (1, .5)), 0.05)
add(sfx, 36.7, whistle(0.6, 1700, 600), 0.1)
add(sfx, 37.3, thump(0.4, 70), 0.35)
add(sfx, 37.4, moo(1.2, 115), 0.35)
for j, nt in enumerate([72, 76, 79, 84]):
    add(sfx, 37.7 + j * 0.11, tone(hz(nt), 0.8, 0.3, (1, .3)), 0.18)

mix = music + sfx
mix /= np.max(np.abs(mix)) / 0.75
os.makedirs(os.path.join(here, "out"), exist_ok=True)
with wave.open(os.path.join(here, "out", "music_sfx.wav"), "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.stack([mix, mix], 1) * 32767).astype("<i2").tobytes())
print("ok")
