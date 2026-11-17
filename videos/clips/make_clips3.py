"""Mittellange Clips: je 3 Wörter hintereinander (15–18 s) mit Hook-Banner und End-Karte.
Nutzung: python3 make_clips3.py  -> clips/3er/<serie>-NN.mp4 + clips/CAPTIONS-3er.md
"""
import json, os, subprocess
from make_clips import SPICY, FF, V, END, HERE  # nutzt dieselben Einstellungen (Import erzeugt keine Clips)

HOOKS_SPICY = ["3 things {who} say when they're ANGRY {flag}😤", "3 words {who} use when things go WRONG {flag}🌶️",
               "How to swear like {who_s} {flag}😳", "3 {lang} words you WON'T learn in school {flag}"]
LANG = {"spanish-spicy": ("Spanish", "a Spaniard"), "spicy-spanish-2": ("Mexican", "a Mexican"), "spicy-french": ("French", "a French person"),
        "spicy-italian": ("Italian", "an Italian"), "spicy-portuguese": ("Brazilian", "a Brazilian")}
od = os.path.join(HERE, "3er"); os.makedirs(od, exist_ok=True)
jobs, clips, caps = [], [], []
end_png = os.path.join(od, "_end.png")
jobs.append(dict(out=end_png, kind="end", l1="FOLLOW FOR MORE 🐥", l2="New words every day!"))
for series, cfg in list(SPICY.items()) + list(FF.items()):
    tl = json.load(open(os.path.join(V, series, "timeline.json")))
    src = os.path.join(V, series, "out", f"{series}-stimme.mp4")
    ff = series in FF
    who, flag, tags = cfg
    for g in range(len(tl["words"]) // 3):
        k = g * 3
        words = tl["words"][k:k + 3]
        start = tl["intro"] + k * tl["per"]; dur = 3 * tl["per"] - 0.3
        if ff:
            l1 = ["3 Spanish words that TRICK English speakers 😳", "Don't say these in Spain! 🇪🇸😳",
                  "You're using these Spanish words WRONG 🤦", "3 Spanish words that DON'T mean what you think 🇪🇸"][g % 4]
            l2 = "Number 3 is the worst 😂"
            cap = f"{l1} Which one fooled you? 👇\n\n{tags}"
        else:
            lang, who_s = LANG[series]
            l1 = HOOKS_SPICY[g % 4].format(who=who, flag=flag, who_s=who_s, lang=lang)
            l2 = "🌶️ Wait for number 3…"
            cap = f"{l1} Which one is your favorite? 😂 (Not for kids!)\n\n{tags}"
        base = f"{series}-{g + 1:02d}"
        hook = os.path.join(od, f"_{base}.png")
        jobs.append(dict(out=hook, kind="hook", l1=l1, l2=l2))
        clips.append((src, start, dur, hook, os.path.join(od, base + ".mp4")))
        caps.append((base + ".mp4", ", ".join((w.get("es") or w.get("w")) for w in words), cap))
jf = os.path.join(HERE, "_jobs3.json"); json.dump(jobs, open(jf, "w"), ensure_ascii=False)
subprocess.run(["node", os.path.join(HERE, "overlay.mjs"), jf], check=True); os.remove(jf)
for src, start, dur, hook, out in clips:
    total = dur + END
    fc = (f"[0:v]tpad=stop_mode=clone:stop_duration={END}[v0];[v0][1:v]overlay=0:0:enable='lt(t,{dur})'[v1];"
          f"[v1][2:v]overlay=0:0:enable='gte(t,{dur})'[v];[0:a]afade=t=out:st={dur - 0.25:.2f}:d=0.25,apad=whole_dur={total}[a]")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{start:.2f}", "-t", f"{dur:.2f}", "-i", src, "-loop", "1", "-i", hook,
                    "-loop", "1", "-i", end_png, "-filter_complex", fc, "-map", "[v]", "-map", "[a]", "-t", f"{total:.2f}",
                    "-c:v", "libx264", "-preset", "veryfast", "-crf", "21", "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "160k",
                    "-movflags", "+faststart", out], check=True)
with open(os.path.join(HERE, "CAPTIONS-3er.md"), "w") as f:
    f.write("# 3-Wörter-Clips (15–18 s): Beschreibungen zum Kopieren\n")
    for file, ws, cap in caps: f.write(f"\n**{file}** ({ws})\n```\n{cap}\n```\n")
print("fertig:", len(clips), "Clips")
