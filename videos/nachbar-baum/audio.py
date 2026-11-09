"""Erzeugt Musik + Soundeffekte passend zu timeline.json (ohne Sprecher).
Nutzung: python3 audio.py -> out/music_sfx.wav
"""
import json, wave, os
import numpy as np

SR = 48000
here = os.path.dirname(os.path.abspath(__file__))
tl = json.load(open(os.path.join(here, "timeline.json")))
DUR = tl["duration"]
N = int(DUR * SR)
rng = np.random.default_rng(7)
music = np.zeros(N)
sfx = np.zeros(N)


def add(buf, t, sig, gain=1.0):
    i = int(t * SR)
    if i >= N: return
    sig = sig[: N - i]
    buf[i:i + len(sig)] += sig * gain


def env(n, a=0.005, r=None):
    t = np.arange(n) / SR
    e = np.minimum(1, t / max(a, 1e-4))
    if r: e *= np.exp(-t / r)
    return e


def tone(f, d, r=0.25, harm=(1, .5, .25), a=0.004):
    n = int(d * SR); t = np.arange(n) / SR
    s = sum(h * np.sin(2 * np.pi * f * (k + 1) * t) for k, h in enumerate(harm))
    return s * env(n, a, r)


def noise(d):
    return rng.standard_normal(int(d * SR))


def lowpass(x, a):  # einfacher 1-Pol-Tiefpass, a in (0,1)
    y = np.empty_like(x); acc = 0.0
    for i, v in enumerate(x):
        acc += a * (v - acc); y[i] = acc
    return y


def hz(note):  # MIDI -> Hz
    return 440 * 2 ** ((note - 69) / 12)


# ---------- Musik: lockerer Ukulele/Pluck-Loop, 100 BPM ----------
bpm = 100; beat = 60 / bpm
chords = [[60, 64, 67], [55, 59, 62], [57, 60, 64], [53, 57, 60]]  # C G Am F
t = 0.0; bar = 0
while t < DUR:
    ch = chords[bar % 4]
    for i in range(8):  # Achtel-Arpeggio
        nt = ch[[0, 1, 2, 1, 0, 2, 1, 2][i]] + 12
        add(music, t + i * beat / 2, tone(hz(nt), 0.5, 0.18, (1, .35, .12)), 0.09)
    for b in (0, 2):  # Bass
        add(music, t + b * beat, tone(hz(ch[0] - 24), 0.9, 0.35, (1, .3)), 0.22)
    for b in range(4):  # Kick
        n = int(0.25 * SR); tt = np.arange(n) / SR
        add(music, t + b * beat, np.sin(2 * np.pi * (50 + 90 * np.exp(-tt * 30)) * tt) * np.exp(-tt * 14), 0.35)
        add(music, t + (b + .5) * beat, noise(0.05) * env(int(0.05 * SR), 0.001, 0.012), 0.05)  # Hi-Hat
    t += 4 * beat; bar += 1
# Musik im Sturm abdunkeln, am Ende ausblenden
tt = np.arange(N) / SR
duck = 1 - 0.65 * (np.clip((tt - 6.6) / 0.5, 0, 1) * np.clip((10.4 - tt) / 0.5, 0, 1))
fade = np.clip((DUR - tt) / 1.2, 0, 1) * np.clip(tt / 0.3, 0, 1)
music *= duck * fade

# ---------- Soundeffekte ----------
def whoosh(d=0.5):
    n = int(d * SR); x = lowpass(noise(d), 0.08)
    e = np.sin(np.pi * np.arange(n) / n) ** 2
    return x * e


def popfx(f=520):
    n = int(0.12 * SR); t_ = np.arange(n) / SR
    return np.sin(2 * np.pi * (f + 900 * np.exp(-t_ * 40)) * t_) * np.exp(-t_ * 30)


for k in [2.75, 6.15, 9.75, 15.05, 21.25, 27.35, 32.35]:
    add(sfx, k, whoosh(0.55), 0.35)
for k in [10.6, 12.0, 15.4, 18.2, 22.4, 28.3, 32.6]:
    add(sfx, k, popfx(), 0.35)

# Ast wächst: knarzen
cr = lowpass(noise(2.4), 0.2) * (0.6 + 0.4 * np.sign(np.sin(2 * np.pi * 9 * np.arange(int(2.4 * SR)) / SR)))
add(sfx, 0.1, cr * env(len(cr), 0.3) * np.linspace(1, 0.2, len(cr)), 0.12)
# Laub raschelt
rs = noise(3.2) - lowpass(noise(3.2), 0.3)
add(sfx, 3.1, rs * np.sin(np.pi * np.arange(len(rs)) / len(rs)), 0.06)
# Regen + Wind
d = 4.0; rain = noise(d) - lowpass(noise(d), 0.5)
wind = lowpass(noise(d), 0.01) * (1 + 0.5 * np.sin(2 * np.pi * 0.7 * np.arange(int(d * SR)) / SR))
e = np.clip(np.arange(int(d * SR)) / SR / 0.5, 0, 1) * np.clip((d - np.arange(int(d * SR)) / SR) / 0.6, 0, 1)
add(sfx, 6.5, (rain * 0.09 + wind * 1.6) * e, 1.0)
# Donner
th = lowpass(noise(2.2), 0.01) * env(int(2.2 * SR), 0.02, 0.6)
add(sfx, 7.5, th, 6.0)
add(sfx, 7.5, noise(0.15) * env(int(.15 * SR), 0.001, 0.04), 0.4)
# Ziegel lösen sich / schlagen auf
for k in [8.25, 8.75, 9.25]:
    add(sfx, k, popfx(300), 0.25)
for k in [9.15, 9.65, 10.15]:
    clank = sum(tone(f, 0.3, 0.08, (1,)) for f in (820, 1130, 1570)) / 3
    add(sfx, k, clank + lowpass(noise(0.3), 0.3) * env(int(.3 * SR), 0.001, 0.05), 0.45)
# Säge-Versuch + "Falsch"-Summer
for k, f in [(12.05, 330), (12.3, 262)]:
    n = int(0.22 * SR); t_ = np.arange(n) / SR
    add(sfx, k, np.sign(np.sin(2 * np.pi * f * t_)) * env(n, 0.005, 0.15), 0.12)
# Brief fliegt
add(sfx, 16.3, whoosh(0.9), 0.3)
# Uhr tickt + Ding
for i, k in enumerate(np.arange(18.5, 21.8, 0.25)):
    add(sfx, k, tone(2200 if i % 2 else 1800, 0.04, 0.01, (1,)), 0.25)
add(sfx, 21.85, tone(hz(84), 1.2, 0.5, (1, .4, .2)), 0.25)
# Fragezeichen: "hmm?"-Glissando
n = int(0.45 * SR); t_ = np.arange(n) / SR
add(sfx, 22.45, np.sin(2 * np.pi * (300 * t_ + 300 * t_ ** 2)) * env(n, 0.02, 0.25), 0.18)
# Ast stört: Warn-Piepser
for k in [25.3, 25.8, 26.3, 26.8]:
    add(sfx, k, tone(1046, 0.15, 0.06, (1, .2)), 0.15)
# Sägen
d = 1.4; n = int(d * SR); t_ = np.arange(n) / SR
rasp = (noise(d) - lowpass(noise(d), 0.4)) * (0.35 + 0.65 * np.abs(np.sin(22 * t_)))
add(sfx, 28.9, rasp * env(n, 0.03), 0.22)
# Ast knackt + fällt + Aufprall
add(sfx, 30.3, noise(0.12) * env(int(.12 * SR), 0.001, 0.03), 0.6)
add(sfx, 30.4, whoosh(0.9), 0.4)
n = int(0.6 * SR); t_ = np.arange(n) / SR
add(sfx, 31.4, np.sin(2 * np.pi * (45 + 60 * np.exp(-t_ * 20)) * t_) * np.exp(-t_ * 7) + lowpass(noise(0.6), 0.1) * np.exp(-t_ * 9) * 1.5, 0.7)
# Erfolg-Jingle
for i, nt in enumerate([72, 76, 79, 84]):
    add(sfx, 32.6 + i * 0.11, tone(hz(nt), 0.8, 0.3, (1, .3)), 0.18)

mix = music + sfx
mix /= max(1e-9, np.max(np.abs(mix))) / 0.7  # Spitze bei ca. -3 dBFS
stereo = np.stack([mix, mix], axis=1)
os.makedirs(os.path.join(here, "out"), exist_ok=True)
with wave.open(os.path.join(here, "out", "music_sfx.wav"), "wb") as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes((stereo * 32767).astype("<i2").tobytes())
print("ok", DUR, "s")
