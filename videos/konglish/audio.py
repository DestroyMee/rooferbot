"""Musik + Soundeffekte für Konglish (Stimmen kommen über ../voice_mix.py).
Nutzung: python3 audio.py -> out/music_sfx.wav
"""
import json, os, wave
import numpy as np

SR = 48000
here = os.path.dirname(os.path.abspath(__file__))
TL = json.load(open(os.path.join(here, "timeline.json")))
DUR, I0, PER, NW = TL["duration"], TL["intro"], TL["per"], len(TL["words"])
T_A, T_B, T_R = 0.9, 0.45, 2.5
N = int(DUR * SR); rng = np.random.default_rng(11)
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
    t = ts(0.13); return np.sin(2 * np.pi * (f + 1000 * np.exp(-t * 35)) * t) * np.exp(-t * 26)


def buzzer():  # "Äh-äh"
    out = np.zeros(int(0.5 * SR))
    for k, st in enumerate((0, 0.26)):
        t = ts(0.2); s = np.sign(np.sin(2 * np.pi * (150 - 20 * k) * t)) * np.minimum(1, t / 0.01) * np.clip((0.2 - t) / 0.03, 0, 1)
        i = int(st * SR); out[i:i + len(s)] += s
    return out


def whoosh(d=0.4):
    x = rng.standard_normal(int(d * SR)); y = np.empty_like(x); acc = 0.0
    for i, v in enumerate(x): acc += 0.12 * (v - acc); y[i] = acc
    return y * np.sin(np.pi * np.arange(len(y)) / len(y)) ** 2


# Musik: verspieltes Pizzicato-Thema, 116 BPM, leise
beat = 60 / 116
chords = [[62, 66, 69], [67, 71, 74], [64, 67, 71], [69, 73, 76]]
mel = [74, 76, 78, 74, 79, None, 78, 76, 74, 71, 72, 74, 76, None, 74, None]
t = 0.0; i = 0
while t < DUR:
    ch = chords[(i // 4) % 4]
    add(music, t, tone(hz(ch[0] - 24), 0.4, 0.12, (1, .5, .2)), 0.25)
    add(music, t + beat / 2, tone(hz(ch[0] - 17), 0.3, 0.08, (1, .4)), 0.12)
    for j, n_ in enumerate(ch): add(music, t + beat / 2, tone(hz(n_), 0.2, 0.05, (1, .4, .2)), 0.04)
    if mel[i % 16] and (i // 16) % 2 == 0: add(music, t, tone(hz(mel[i % 16]), 0.25, 0.08, (1, .3, .1)), 0.07)
    t += beat; i += 1
tt = np.arange(N) / SR
music *= np.clip(tt / 0.3, 0, 1) * np.clip((DUR - tt) / 1.2, 0, 1)

for j, n_ in enumerate([74, 78, 81, 86]): add(sfx, 0.15 + j * 0.09, bell(hz(n_)), 0.2)
for k in range(NW):
    s0 = I0 + k * PER
    add(sfx, s0 + 0.1, popfx(500), 0.3)
    add(sfx, s0 + T_A, popfx(380), 0.25)
    add(sfx, s0 + T_B, popfx(460), 0.25)
    add(sfx, s0 + T_R, bell(hz(88)), 0.18); add(sfx, s0 + T_R + 0.08, bell(hz(93)), 0.15)
    for j in range(3): add(sfx, s0 + T_R + 0.3 + j * 0.13, tone(hz(84 - 3 * j), 0.12, 0.05, (1, .4)), 0.08)  # "ha-ha-ha"
    add(sfx, s0 + PER - 0.32, whoosh(0.4), 0.25)
o = I0 + NW * PER
for j, n_ in enumerate([67, 72, 76, 79, 84]): add(sfx, o + 0.05 + j * 0.1, tone(hz(n_), 0.9, 0.35, (1, .6, .4, .2)), 0.16)

mix = music + sfx; mix /= np.max(np.abs(mix)) / 0.7
os.makedirs(os.path.join(here, "out"), exist_ok=True)
with wave.open(os.path.join(here, "out", "music_sfx.wav"), "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.stack([mix, mix], 1) * 32767).astype("<i2").tobytes())
print("ok")
