"""Musik + Soundeffekte für die Spicy-Serie (ohne Stimmen; die kommen über ../voice_mix.py).
Nutzung: python3 audio.py -> out/music_sfx.wav
"""
import json, os, wave
import numpy as np

SR = 48000
here = os.path.dirname(os.path.abspath(__file__))
TL = json.load(open(os.path.join(here, "timeline.json")))
DUR, I0, PER, W = TL["duration"], TL["intro"], TL["per"], TL["words"]
REACT = 1.3
N = int(DUR * SR); rng = np.random.default_rng(9)
music = np.zeros(N); sfx = np.zeros(N)


def add(buf, t, sig, g=1.0):
    i = int(t * SR)
    if 0 <= i < N: s = sig[: N - i]; buf[i:i + len(s)] += s * g


def ts(d): return np.arange(int(d * SR)) / SR
def hz(n): return 440 * 2 ** ((n - 69) / 12)
def noise(d): return rng.standard_normal(int(d * SR))


def lowpass(x, a):
    y = np.empty_like(x); acc = 0.0
    for i, v in enumerate(x): acc += a * (v - acc); y[i] = acc
    return y


def tone(f, d, r=0.25, harm=(1, .5, .25), a=0.004):
    t = ts(d); s = sum(h * np.sin(2 * np.pi * f * (k + 1) * t) for k, h in enumerate(harm))
    return s * np.minimum(1, t / a) * np.exp(-t / r)


def pluck(f, d=0.6):  # Karplus-Strong-Gitarre
    n = int(d * SR); p = max(2, int(SR / f)); buf = rng.uniform(-1, 1, p); out = np.zeros(n)
    for i in range(n):
        out[i] = buf[i % p]; buf[i % p] = 0.5 * (buf[i % p] + buf[(i + 1) % p]) * 0.996
    return out


def popfx(f=500):
    t = ts(0.13); return np.sin(2 * np.pi * (f + 1000 * np.exp(-t * 35)) * t) * np.exp(-t * 26)


def slam():
    t = ts(0.5)
    return np.sin(2 * np.pi * (50 + 120 * np.exp(-t * 18)) * t) * np.exp(-t * 7) + lowpass(noise(0.5), 0.2) * np.exp(-t * 20) * 1.5


def whoosh(d=0.4):
    y = lowpass(noise(d), 0.1); return y * np.sin(np.pi * np.arange(len(y)) / len(y)) ** 2


# ---------- Musik: verspielter Latin-Groove (Gitarre, Bass, Shaker, Clave), 108 BPM ----------
beat = 60 / 108
prog = [[57, 60, 64], [62, 65, 69], [64, 68, 71], [57, 60, 64]]  # Am Dm E Am
cache = {}
def P(n):
    if n not in cache: cache[n] = pluck(hz(n), 0.5)
    return cache[n]
t = 0.0; b = 0
while t < DUR:
    ch = prog[(b // 4) % 4]
    add(music, t, tone(hz(ch[0] - 24), 0.4, 0.15, (1, .4)), 0.25)
    if b % 2: add(music, t + beat / 2, tone(hz(ch[0] - 17), 0.3, 0.1, (1, .4)), 0.15)
    for j, n_ in enumerate(ch): add(music, t + beat * 0.5 + j * 0.015, P(n_ + 12), 0.10)
    if b % 4 in (0, 2): add(music, t + beat * 0.75, P(ch[-1] + 12), 0.08)
    for k in range(4): add(music, t + k * beat / 4, noise(0.04) * np.exp(-ts(0.04) * 90), 0.025 + 0.02 * (k == 2))
    if b % 8 in (0, 1, 3, 5, 6): add(music, t + (0.5 if b % 2 else 0) * beat, tone(2500, 0.05, 0.015, (1,)), 0.06)
    t += beat; b += 1
tt = np.arange(N) / SR
music *= np.clip(tt / 0.3, 0, 1) * np.clip((DUR - tt) / 1.2, 0, 1)

# ---------- Effekte ----------
add(sfx, 0.15, slam(), 0.4)
add(sfx, 0.2, popfx(350), 0.3)
for k, w in enumerate(W):
    s0 = I0 + k * PER
    add(sfx, s0, popfx(450 + 30 * k), 0.3)
    add(sfx, s0 + REACT, slam(), 0.55)                # Wort knallt rein
    add(sfx, s0 + REACT + 0.4, popfx(800), 0.15)      # Region-Schild
    for c in range(w["spice"]): add(sfx, s0 + REACT + 0.55 + c * 0.09, tone(hz(84 + 3 * c), 0.15, 0.05, (1, .3)), 0.1)
    add(sfx, s0 + 2.6, popfx(650), 0.18)
    add(sfx, s0 + PER - 0.32, whoosh(0.4), 0.25)
    p = w["pic"]
    if p == "toe": add(sfx, s0 + 0.9, slam(), 0.4); add(sfx, s0 + 0.95, tone(1800, 0.6, 0.2, (1,)), 0.05)
    if p == "phone": add(sfx, s0 + 0.85, lowpass(noise(0.4), 0.6) * np.exp(-ts(0.4) * 9), 0.5)
    if p == "bill":
        x = noise(1.0) * (np.sin(2 * np.pi * 30 * ts(1.0)) > 0.5); add(sfx, s0 + 0.2, (x - lowpass(x, 0.3)) * 0.4)
        add(sfx, s0 + 1.2, tone(1320, 0.3, 0.08) + tone(1980, 0.3, 0.08), 0.12)
    if p == "bus":
        e = lowpass(noise(1.6), 0.02) * np.linspace(1, 0.1, int(1.6 * SR)); add(sfx, s0, e, 3.0)
        add(sfx, s0 + 0.3, tone(330, 0.5, 0.4, (1, .8, .6)) + tone(415, 0.5, 0.4, (1, .8, .6)), 0.06)
    if p == "toast": add(sfx, s0 + 0.7, popfx(300), 0.5); add(sfx, s0 + 0.75, tone(hz(88), 0.8, 0.3, (1, .3)), 0.12)
    if p == "line": add(sfx, s0 + 0.3, whoosh(0.7), 0.4); add(sfx, s0 + 1.0, popfx(250), 0.3)
    if p == "splash":
        add(sfx, s0 + 0.1, lowpass(noise(1.0), 0.03) * np.sin(np.pi * ts(1.0)), 2.0)
        add(sfx, s0 + 0.5, (noise(0.6) - lowpass(noise(0.6), 0.4)) * np.exp(-ts(0.6) * 5), 0.45)
    if p == "fries":
        for j in range(8): add(sfx, s0 + 0.2 + j * 0.16, (noise(0.06) - lowpass(noise(0.06), 0.5)) * np.exp(-ts(0.06) * 60), 0.35)
    if p == "wifi":
        for j in range(2): add(sfx, s0 + 0.6 + j * 0.18, np.sign(np.sin(2 * np.pi * 180 * ts(0.14))) * np.exp(-ts(0.14) * 8), 0.08)
    if p == "icecream": add(sfx, s0 + 0.85, lowpass(noise(0.25), 0.15) * np.exp(-ts(0.25) * 14), 1.2); add(sfx, s0 + 0.86, popfx(220), 0.3)
    if p == "alarm":
        r = np.sin(2 * np.pi * 2200 * ts(1.8)) * (np.sin(2 * np.pi * 18 * ts(1.8)) > 0) * np.clip((1.8 - ts(1.8)) / 0.2, 0, 1)
        add(sfx, s0 + 0.05, r, 0.07)
    if p == "rain":
        x = noise(3.0) - lowpass(noise(3.0), 0.4); e = np.clip((ts(3.0) - 0.2) / 0.6, 0, 1) * np.clip((3.0 - ts(3.0)) / 0.5, 0, 1)
        add(sfx, s0 + 0.2, x * e, 0.12)
o = I0 + len(W) * PER
for j, n_ in enumerate([69, 73, 76, 81]): add(sfx, o + 0.1 + j * 0.1, pluck(hz(n_), 0.8), 0.18)

mix = music + sfx; mix /= np.max(np.abs(mix)) / 0.7
os.makedirs(os.path.join(here, "out"), exist_ok=True)
with wave.open(os.path.join(here, "out", "music_sfx.wav"), "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((np.stack([mix, mix], 1) * 32767).astype("<i2").tobytes())
print("ok")
