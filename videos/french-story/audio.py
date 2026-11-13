"""Musik + Soundeffekte für 'À la boulangerie' (ohne Sprecher).
Nutzung: python3 audio.py -> out/music_sfx.wav
"""
import json, os, wave
import numpy as np

SR = 48000
here = os.path.dirname(os.path.abspath(__file__))
TL = json.load(open(os.path.join(here, "timeline.json")))
DUR, I0, PER = TL["duration"], TL["intro"], TL["per"]
QS, OUT = TL["quiz"]["start"], TL["outro"]
N = int(DUR * SR); rng = np.random.default_rng(5)
music = np.zeros(N); sfx = np.zeros(N)


def add(buf, t, sig, g=1.0):
    i = int(t * SR)
    if 0 <= i < N: s = sig[: N - i]; buf[i:i + len(s)] += s * g


def ts(d): return np.arange(int(d * SR)) / SR
def hz(n): return 440 * 2 ** ((n - 69) / 12)


def tone(f, d, r=0.25, harm=(1, .5, .25), a=0.004, vib=0.0):
    t = ts(d); ph = 2 * np.pi * f * (t + vib * np.sin(2 * np.pi * 5.5 * t) / (2 * np.pi * 5.5))
    s = sum(h * np.sin(ph * (k + 1)) for k, h in enumerate(harm))
    return s * np.minimum(1, t / a) * np.exp(-t / r)


def accordion(f, d):  # zwei leicht verstimmte Zungen = Musette-Klang
    t = ts(d); e = np.minimum(1, t / 0.03) * np.clip((d - t) / 0.06, 0, 1)
    s = 0
    for det in (1.0, 1.006):
        ph = 2 * np.pi * f * det * t
        s = s + np.sin(ph) + .5 * np.sin(2 * ph) + .35 * np.sin(3 * ph) + .2 * np.sin(4 * ph)
    return s * e * 0.5


def bell(f, d=0.9): return tone(f, d, 0.4, (1, 0, .45, 0, .2))
def popfx(f=500):
    t = ts(0.13); return np.sin(2 * np.pi * (f + 1000 * np.exp(-t * 35)) * t) * np.exp(-t * 26)
def click(f=1800):
    t = ts(0.03); return np.sin(2 * np.pi * f * t) * np.exp(-t * 180)


# ---------- Musik: Walzer im 3/4-Takt ----------
beat = 60 / 168
prog = [(57, [60, 64, 69]), (52, [59, 64, 68]), (57, [60, 64, 69]), (50, [57, 62, 65]),
        (52, [59, 64, 68]), (57, [60, 64, 69]), (52, [59, 62, 68]), (57, [60, 64, 69])]
mel = [76, 77, 76, 74, 72, 71, 72, 74, 76, 69, 71, 72, 74, 76, 74, 72, 71, 69, 71, 72, 74, 76, 74, 72]
t = 0.0; bar = 0
while t < DUR:
    root, ch = prog[bar % 8]
    add(music, t, tone(hz(root - 12), 0.45, 0.2, (1, .4, .2)), 0.22)
    for b in (1, 2):
        for n_ in ch: add(music, t + b * beat, tone(hz(n_), 0.22, 0.08, (1, .5, .3)), 0.035)
    for b in range(3):
        m = mel[(bar * 3 + b) % 24]
        add(music, t + b * beat, accordion(hz(m), beat * 0.95), 0.05)
    t += 3 * beat; bar += 1
tt = np.arange(N) / SR
# leiser während des Quiz-Countdowns, damit das Ticken wirkt
duck = 1 - 0.6 * np.clip((tt - (QS + 1.6)) / 0.3, 0, 1) * np.clip((QS + 5.0 - tt) / 0.3, 0, 1)
music *= duck * np.clip(tt / 0.4, 0, 1) * np.clip((DUR - tt) / 1.2, 0, 1)

# ---------- Effekte ----------
for j, n_ in enumerate([88, 84]): add(sfx, 0.5 + j * 0.25, bell(hz(n_), 1.2), 0.2)   # Türglocke
for k in range(9):                                                                    # Schritte
    add(sfx, 0.3 + k * 0.26, click(300 + (k % 2) * 60) * 3, 0.12)
for i, line in enumerate(TL["lines"]):
    s0 = I0 + i * PER
    fr = "".join(p[0] if isinstance(p, list) else p for p in line["fr"])
    add(sfx, s0 + 0.1, popfx(520 if line["who"] == "coco" else 380), 0.3)
    for c in range(len(fr)):                                                          # Tipp-Geräusche
        if fr[c] != " ": add(sfx, s0 + 0.25 + 0.9 * c / len(fr), click(1600 + (c % 3) * 250), 0.06)
    add(sfx, s0 + 1.4, bell(hz(91), 0.5), 0.1)                                         # Übersetzung
ls = lambda i: I0 + i * PER
# Croissant fliegt
t_ = ts(0.9); add(sfx, ls(3) + 0.65, np.sin(2 * np.pi * np.cumsum(500 + 700 * t_ / 0.9) / SR) * np.sin(np.pi * t_ / 0.9), 0.08)
# Ka-ching
add(sfx, ls(3) + 1.0, tone(1320, 0.25, 0.08, (1, .6, .3)), 0.15)
add(sfx, ls(3) + 1.08, bell(hz(96), 0.9) + bell(hz(100), 0.9), 0.12)
# Münze
add(sfx, ls(4) + 0.8, tone(2600, 0.5, 0.12, (1, .3)) + tone(3900, 0.4, 0.08, (1,)), 0.1)
# Herzen
for k in range(5): add(sfx, ls(4) + 0.35 + k * 0.18, bell(hz(84 + 3 * k), 0.4), 0.06)
# Quiz
add(sfx, QS, popfx(300), 0.4)
for i in range(3): add(sfx, QS + 0.8 + i * 0.2, popfx(600 + i * 120), 0.25)
for i in range(3): add(sfx, QS + 1.8 + i, tone(1000 if i < 2 else 1400, 0.12, 0.05, (1, .3)), 0.25)
for j, n_ in enumerate([72, 76, 79, 84]): add(sfx, QS + 4.9 + j * 0.08, bell(hz(n_)), 0.2)  # richtig!
# Outro
add(sfx, OUT, popfx(450), 0.35)
for j, n_ in enumerate([69, 73, 76, 81]): add(sfx, OUT + 0.1 + j * 0.12, accordion(hz(n_), 0.5), 0.12)

mix = music + sfx; mix /= np.max(np.abs(mix)) / 0.7
os.makedirs(os.path.join(here, "out"), exist_ok=True)
with wave.open(os.path.join(here, "out", "music_sfx.wav"), "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.stack([mix, mix], 1) * 32767).astype("<i2").tobytes())
print("ok")
