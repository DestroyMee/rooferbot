"""Musik + Soundeffekte für French Basics (ohne Sprecher).
Nutzung: python3 audio.py -> out/music_sfx.wav
"""
import json, os, wave
import numpy as np

SR = 48000
here = os.path.dirname(os.path.abspath(__file__))
TL = json.load(open(os.path.join(here, "timeline.json")))
DUR, I0, PER, NW = TL["duration"], TL["intro"], TL["per"], len(TL["words"])
N = int(DUR * SR); rng = np.random.default_rng(3)
music = np.zeros(N); sfx = np.zeros(N)


def add(buf, t, sig, g=1.0):
    i = int(t * SR)
    if 0 <= i < N: s = sig[: N - i]; buf[i:i + len(s)] += s * g


def ts(d): return np.arange(int(d * SR)) / SR
def hz(n): return 440 * 2 ** ((n - 69) / 12)


def tone(f, d, r=0.25, harm=(1, .5, .25), a=0.004):
    t = ts(d); s = sum(h * np.sin(2 * np.pi * f * (k + 1) * t) for k, h in enumerate(harm))
    return s * np.minimum(1, t / a) * np.exp(-t / r)


def bell(f, d=0.8): return tone(f, d, 0.35, (1, 0, .4, 0, .15))


def popfx(f=500):
    t = ts(0.14); return np.sin(2 * np.pi * (f + 1100 * np.exp(-t * 35)) * t) * np.exp(-t * 26)


def whoosh(d=0.4):
    x = rng.standard_normal(int(d * SR)); y = np.empty_like(x); acc = 0.0
    for i, v in enumerate(x): acc += 0.12 * (v - acc); y[i] = acc
    return y * np.sin(np.pi * np.arange(len(y)) / len(y)) ** 2


# Musik: fröhliches Glockenspiel + Ukulele + Bass, 112 BPM, leise (Platz für die Stimme)
beat = 60 / 112
chords = [[60, 64, 67], [65, 69, 72], [67, 71, 74], [60, 64, 67]]
mel = [79, 76, 79, 81, 79, 76, 72, 74, 77, 81, 79, 77, 76, 74, 72, None]
t = 0.0; i = 0
while t < DUR:
    ch = chords[(i // 4) % 4]
    add(music, t, tone(hz(ch[0] - 24), 0.5, 0.2, (1, .3)), 0.25)
    for j, n_ in enumerate(ch): add(music, t + beat / 2 + j * 0.012, tone(hz(n_), 0.3, 0.1, (1, .4, .2)), 0.05)
    if mel[i % 16] and (i // 16) % 2 == 0: add(music, t, bell(hz(mel[i % 16])), 0.06)
    add(music, t + beat / 2, rng.standard_normal(int(.03 * SR)) * np.exp(-ts(.03) * 120), 0.03)
    t += beat; i += 1
tt = np.arange(N) / SR
music *= np.clip(tt / 0.3, 0, 1) * np.clip((DUR - tt) / 1.2, 0, 1)

# Intro
for j, n_ in enumerate([72, 76, 79, 84]): add(sfx, 0.15 + j * 0.09, bell(hz(n_)), 0.2)
add(sfx, 0.0, popfx(400), 0.4)
# Pro Wort
for k in range(NW):
    s0 = I0 + k * PER
    add(sfx, s0, popfx(450 + 20 * k), 0.35)               # Karte kommt
    add(sfx, s0 + 0.25, tone(hz(84 + (k % 5) * 2), 0.15, 0.05, (1, .3)), 0.08)  # Buchstaben
    add(sfx, s0 + 1.7, bell(hz(88)), 0.18); add(sfx, s0 + 1.74, bell(hz(91)), 0.14)  # Übersetzung "Ding"
    add(sfx, s0 + 2.6, popfx(700), 0.2)                     # Repeat!
    add(sfx, s0 + PER - 0.32, whoosh(0.4), 0.25)            # Wechsel
# Outro: Fanfare + Konfetti
o = I0 + NW * PER
for j, n_ in enumerate([67, 72, 76, 79, 84]): add(sfx, o + 0.05 + j * 0.1, tone(hz(n_), 0.9, 0.35, (1, .6, .4, .2)), 0.16)
for j in range(18): add(sfx, o + 0.1 + rng.random() * 1.5, popfx(600 + rng.random() * 800), 0.08)

mix = music + sfx; mix /= np.max(np.abs(mix)) / 0.7
os.makedirs(os.path.join(here, "out"), exist_ok=True)
with wave.open(os.path.join(here, "out", "music_sfx.wav"), "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.stack([mix, mix], 1) * 32767).astype("<i2").tobytes())
print("ok")
