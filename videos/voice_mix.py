"""Legt KI-Stimmen (Kokoro, lokal) auf ein fertiges Video.

Nutzung:  python3 videos/voice_mix.py french-basics
          python3 videos/voice_mix.py french-story

Braucht:  pip install kokoro-onnx soundfile
          Modell-Dateien kokoro-v1.0.onnx + voices-v1.0.bin (GitHub-Release von thewh1teagle/kokoro-onnx),
          Pfad über die Umgebungsvariable KOKORO_DIR (Standard: ./kokoro).
Ergebnis: videos/<name>/out/<name>-stimme.mp4
"""
import hashlib, json, os, subprocess, sys, wave
import numpy as np
import soundfile as sf

HERE = os.path.dirname(os.path.abspath(__file__))
SR = 48000
KDIR = os.environ.get("KOKORO_DIR", os.path.join(HERE, "..", "kokoro"))

# Rollen: Kokoro-Stimme, Sprache, Sprechtempo, Tonhöhen-Faktor (>1 = höher und schneller)
ROLES = {
    "fr":       dict(voice="ff_siwis", lang="fr-fr", speed=0.95, pitch=1.0),
    "en":       dict(voice="af_heart", lang="en-us", speed=1.0,  pitch=1.0),
    "coco":     dict(voice="ff_siwis", lang="fr-fr", speed=0.85, pitch=1.22),
    "minou":    dict(voice="ff_siwis", lang="fr-fr", speed=1.0,  pitch=0.93),
    "narrator": dict(voice="af_heart", lang="en-us", speed=1.05, pitch=1.0),
    "es":       dict(voice="em_alex",  lang="es",    speed=0.95, pitch=1.0),
    "sit":      dict(voice="af_heart", lang="en-us", speed=1.25, pitch=1.0),
    "es_f":     dict(voice="ef_dora",  lang="es",    speed=0.95, pitch=1.0),
    "it":       dict(voice="if_sara",  lang="it",    speed=0.95, pitch=1.0),
    "it_m":     dict(voice="im_nicola", lang="it",   speed=0.95, pitch=1.0),
    "pt":       dict(voice="pm_alex",  lang="pt-br", speed=0.95, pitch=1.0),
}

_k = None
def kokoro():
    global _k
    if _k is None:
        from kokoro_onnx import Kokoro
        _k = Kokoro(os.path.join(KDIR, "kokoro-v1.0.onnx"), os.path.join(KDIR, "voices-v1.0.bin"))
    return _k


def synth(text, role, cache):
    if role == "bleep":  # Zensur-Piep, text = Länge in Sekunden
        t = np.arange(int(float(text) * SR)) / SR
        return 0.35 * np.sin(2 * np.pi * 1000 * t) * np.clip(t / 0.01, 0, 1) * np.clip((t[-1] - t) / 0.01, 0, 1)
    r = ROLES[role]
    key = hashlib.md5(json.dumps([text, r]).encode()).hexdigest()[:16]
    f = os.path.join(cache, key + ".wav")
    if not os.path.exists(f):
        a, sr = kokoro().create(text, voice=r["voice"], speed=r["speed"], lang=r["lang"])
        a = np.asarray(a, dtype=np.float64)
        # Stille vorn/hinten abschneiden
        idx = np.where(np.abs(a) > 0.01)[0]
        if len(idx): a = a[max(0, idx[0] - int(0.02 * sr)): idx[-1] + int(0.06 * sr)]
        # auf 48 kHz bringen, dabei Tonhöhe verschieben (Faktor > 1: höher + schneller)
        n_out = int(len(a) * SR / sr / r["pitch"])
        a = np.interp(np.linspace(0, len(a) - 1, n_out), np.arange(len(a)), a)
        sf.write(f, a, SR)
    a, _ = sf.read(f)
    return a


def cues_french_basics(tl):
    c = [dict(t=0.25, limit=3.4, role="en", text="French for beginners! Ten words. Let's go!")]
    for k, w in enumerate(tl["words"]):
        s = tl["intro"] + k * tl["per"]
        c += [dict(t=s + 0.3, limit=s + 1.65, role="fr", text=w["fr"]),
              dict(t=s + 1.7, limit=s + 2.65, role="en", text=w["en"] + "."),
              dict(t=s + 2.7, limit=s + 3.95, role="fr", text=w["fr"] + "!")]
    o = tl["intro"] + len(tl["words"]) * tl["per"]
    c += [dict(t=o + 0.15, limit=o + 1.2, role="fr", text="Très bien !"),
          dict(t=o + 1.25, limit=tl["duration"] - 0.1, role="en", text="Very good! Follow for part two!")]
    return c


def cues_french_story(tl):
    txt = lambda ps: "".join(p[0] if isinstance(p, list) else p for p in ps)
    c = [dict(t=0.3, limit=3.15, role="narrator", text="Learn French with a story! At the bakery.")]
    for i, l in enumerate(tl["lines"]):
        s = tl["intro"] + i * tl["per"]
        c += [dict(t=s + 0.25, limit=s + 2.2, role=l["who"], text=txt(l["fr"])),
              dict(t=s + 1.9, limit=s + tl["per"] - 0.1, role="narrator", text=txt(l["en"]))]
    q = tl["quiz"]["start"]
    c += [dict(t=q + 0.2, limit=q + 0.75, role="narrator", text="Quiz!"),
          dict(t=q + 0.8, limit=q + 1.8, role="fr", text="Merci beaucoup ?"),
          dict(t=q + 1.8, limit=q + 2.6, role="narrator", text="Three…"),
          dict(t=q + 2.8, limit=q + 3.6, role="narrator", text="Two…"),
          dict(t=q + 3.8, limit=q + 4.6, role="narrator", text="One…"),
          dict(t=q + 4.9, limit=tl["outro"] - 0.05, role="narrator", text="B! Thank you very much!"),
          dict(t=tl["outro"] + 0.1, limit=tl["outro"] + 0.75, role="narrator", text="Comment"),
          dict(t=tl["outro"] + 0.7, limit=tl["outro"] + 1.5, role="fr", text="Bonjour !"),
          dict(t=tl["outro"] + 1.5, limit=tl["duration"] - 0.1, role="narrator",
               text="if you learned something!")]
    return c


def cues_spanish_spicy(tl):
    V = (tl.get("meta") or {}).get("voice") or dict(role="es", intro="Spanish curse words they don't teach you in school!",
                                                   outro_native="¿Cuál es tu favorita?", outro_en="Comment below!")
    c = [dict(t=0.3, limit=3.4, role="en", text=V["intro"])]
    for k, w in enumerate(tl["words"]):
        s = tl["intro"] + k * tl["per"]
        c += [dict(t=s + 0.05, limit=s + 1.25, role="sit", text=w["sit"]),
              dict(t=s + 1.3, limit=s + 2.5, role=V["role"], text=w["es"])]
        if w["spoken"]: c.append(dict(t=s + 2.65, limit=s + tl["per"] - 0.1, role="en", text=w["spoken"]))
        if w["bleep"]: c.append(dict(t=s + 2.7, limit=s + tl["per"] - 0.1, role="bleep", text="0.45"))
    o = tl["intro"] + len(tl["words"]) * tl["per"]
    c += [dict(t=o + 0.2, limit=o + 1.8, role=V["role"], text=V["outro_native"]),
          dict(t=o + 1.9, limit=tl["duration"] - 0.1, role="en", text=V["outro_en"])]
    return c


def cues_basics(tl):
    """Vokabel-Videos aus videos/_basics (Zielsprache aus meta.voice.role)."""
    V = tl["meta"]["voice"]; L = V["role"]
    c = [dict(t=0.25, limit=tl["intro"] - 0.1, role="en", text=V["intro"])]
    for k, w in enumerate(tl["words"]):
        s = tl["intro"] + k * tl["per"]
        c += [dict(t=s + 0.3, limit=s + 1.65, role=L, text=w["fr"]),
              dict(t=s + 1.7, limit=s + 2.65, role="en", text=w["en"].replace(" / ", " or ") + "."),
              dict(t=s + 2.7, limit=s + 3.95, role=L, text=w["fr"] + "!")]
    o = tl["intro"] + len(tl["words"]) * tl["per"]
    c += [dict(t=o + 0.15, limit=o + 1.2, role=L, text=V["outro_native"]),
          dict(t=o + 1.25, limit=tl["duration"] - 0.1, role="en", text=V["outro_en"])]
    return c


BUILDERS = {"french-basics": cues_french_basics, "french-story": cues_french_story, "spanish-spicy": cues_spanish_spicy}


def main(name):
    d = os.path.join(HERE, name); out = os.path.join(d, "out")
    tl = json.load(open(os.path.join(d, "timeline.json")))
    cache = os.path.join(out, "voice_cache"); os.makedirs(cache, exist_ok=True)
    N = int(tl["duration"] * SR)
    voice = np.zeros(N)
    prev_end = 0.0; warn = 0
    builder = BUILDERS.get(name) or (cues_spanish_spicy if name.startswith("spicy") else cues_basics if "meta" in tl else None)
    for cue in builder(tl):
        a = synth(cue["text"], cue["role"], cache)
        start = max(cue["t"], prev_end + 0.1)
        end = start + len(a) / SR
        if end > cue["limit"] + 0.05 or start - cue["t"] > 0.25:
            warn += 1
            print(f"  ! eng: '{cue['text']}' {start:.2f}-{end:.2f}s (geplant ab {cue['t']:.2f}, bis {cue['limit']:.2f})")
        i = int(start * SR); a = a[: N - i]
        voice[i:i + len(a)] += a
        prev_end = end
    voice *= 0.9 / (np.max(np.abs(voice)) + 1e-9)

    # Musik/Effekte unter der Stimme absenken (Ducking)
    with wave.open(os.path.join(out, "music_sfx.wav")) as w:
        bed = np.frombuffer(w.readframes(w.getnframes()), dtype="<i2").reshape(-1, 2)[:, 0] / 32767.0
    bed = np.pad(bed, (0, max(0, N - len(bed))))[:N]
    act = (np.abs(voice) > 0.02).astype(float)
    win = int(0.25 * SR); act = np.convolve(act, np.ones(win) / win, mode="same")
    duck = 1 - 0.6 * np.clip(act * 4, 0, 1)
    mix = voice + bed * 0.75 * duck
    mix *= 0.89 / (np.max(np.abs(mix)) + 1e-9)
    wav = os.path.join(out, "mix_stimme.wav")
    sf.write(wav, np.stack([mix, mix], 1), SR, subtype="PCM_16")
    mp4 = os.path.join(out, f"{name}-stimme.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", os.path.join(out, "frames.mp4"), "-i", wav,
                    "-c:v", "copy", "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", "48000", "-c:a", "aac", "-b:a", "192k", "-shortest", "-movflags", "+faststart", mp4], check=True)
    print(f"fertig: {mp4}  ({warn} Warnungen)")


if __name__ == "__main__":
    main(sys.argv[1])
