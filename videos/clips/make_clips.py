"""Schneidet aus den langen Videos einzelne Kurz-Clips (ein Wort pro Clip) mit Hook-Banner und End-Karte.
Nutzung: python3 make_clips.py   -> clips/<serie>/NN-wort.mp4  +  clips/CAPTIONS.md
"""
import json, os, re, subprocess, unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
V = os.path.join(HERE, "..")
END = 1.3  # Sekunden End-Karte

SPICY = {  # Serie: (Leute, Flagge, Hashtags)
    "spanish-spicy":    ("Spanish speakers", "🇪🇸", "#learnspanish #spanishslang #spanishwords #languagelearning #learnwithcoco"),
    "spicy-spanish-2":  ("Mexicans", "🇲🇽", "#learnspanish #mexicanslang #spanishslang #languagelearning #learnwithcoco"),
    "spicy-french":     ("French people", "🇫🇷", "#learnfrench #frenchslang #frenchwords #languagelearning #learnwithcoco"),
    "spicy-italian":    ("Italians", "🇮🇹", "#learnitalian #italianslang #italianwords #languagelearning #learnwithcoco"),
    "spicy-portuguese": ("Brazilians", "🇧🇷", "#learnportuguese #brazilianportuguese #portugueseslang #languagelearning #learnwithcoco"),
}
FF = {"false-friends-spanish": ("Spain", "🇪🇸", "#learnspanish #spanishwords #falsefriends #languagelearning #learnwithcoco")}


def slug(s):
    s = unicodedata.normalize("NFKD", s).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def sit_to_when(sit):
    s = sit.rstrip("…").rstrip(".")
    return s[0].lower() + s[1:]


def main():
    jobs, clips, captions = [], [], []
    for series, cfg in list(SPICY.items()) + list(FF.items()):
        tl = json.load(open(os.path.join(V, series, "timeline.json")))
        src = os.path.join(V, series, "out", f"{series}-stimme.mp4")
        od = os.path.join(HERE, series); os.makedirs(od, exist_ok=True)
        ff = series in FF
        end_png = os.path.join(od, "_end.png")
        jobs.append(dict(out=end_png, kind="end", l1="FOLLOW FOR MORE 🐥", l2="New words every day!" if ff else "🌶️ More spicy words every day!"))
        for k, w in enumerate(tl["words"]):
            start = tl["intro"] + k * tl["per"]
            dur = tl["per"] - 0.3
            if ff:
                who, flag, tags = cfg
                l1 = f"Think “{w['w']}” means “{w['trap']}”? 🤔"
                l2 = "Most English speakers get this WRONG 😳"
                cap = f"“{w['w']}” does NOT mean “{w['trap']}” 😳{flag} Did you know? Follow for more false friends!\n\n{tags}"
                name = w["w"]
            else:
                who, flag, tags = cfg
                l1 = f"What {who} say when {sit_to_when(w['sit'])} {flag}"
                l2 = "🌶️ They don't teach this in school!"
                cap = f"What {who} REALLY say when {sit_to_when(w['sit'])} 🌶️{flag} Would you say it? 😂 (Not for kids!)\n\n{tags}"
                name = w["es"]
            base = f"{k + 1:02d}-{slug(name)}"
            hook_png = os.path.join(od, f"_{base}.png")
            jobs.append(dict(out=hook_png, kind="hook", l1=l1, l2=l2))
            out = os.path.join(od, base + ".mp4")
            clips.append((src, start, dur, hook_png, end_png, out))
            captions.append((series, base + ".mp4", cap))

    jf = os.path.join(HERE, "_jobs.json"); json.dump(jobs, open(jf, "w"), ensure_ascii=False)
    subprocess.run(["node", os.path.join(HERE, "overlay.mjs"), jf], check=True)

    for src, start, dur, hook_png, end_png, out in clips:
        total = dur + END
        fc = (f"[0:v]tpad=stop_mode=clone:stop_duration={END}[v0];"
              f"[v0][1:v]overlay=0:0:enable='lt(t,{dur})'[v1];"
              f"[v1][2:v]overlay=0:0:enable='gte(t,{dur})'[v];"
              f"[0:a]afade=t=out:st={dur - 0.25:.2f}:d=0.25,apad=whole_dur={total}[a]")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{start:.2f}", "-t", f"{dur:.2f}", "-i", src,
                        "-loop", "1", "-i", hook_png, "-loop", "1", "-i", end_png, "-filter_complex", fc,
                        "-map", "[v]", "-map", "[a]", "-t", f"{total:.2f}", "-c:v", "libx264", "-preset", "veryfast", "-crf", "21",
                        "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k", "-movflags", "+faststart", out], check=True)
        print("clip", os.path.relpath(out, HERE))

    with open(os.path.join(HERE, "CAPTIONS.md"), "w") as f:
        f.write("# Kurz-Clips: Beschreibungen zum Kopieren\n\nJeder Clip: Datei hochladen, Text darunter kopieren. Spicy-Clips nicht als „für Kinder“ markieren.\n")
        cur = None
        for series, file, cap in captions:
            if series != cur: f.write(f"\n## {series}\n"); cur = series
            f.write(f"\n**{file}**\n```\n{cap}\n```\n")
    print("fertig:", len(clips), "Clips")


if __name__ == "__main__":
    main()
