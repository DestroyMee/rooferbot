"""Hook-Versionen der langen Videos: Titel-Intro wird weggeschnitten, das Video startet sofort mit dem ersten Wort,
in den ersten 5 Sekunden steht oben ein Hook-Banner. Länge bleibt über 60 s (TikTok Creator Rewards).
Nutzung: python3 make_hooks.py  -> hooks/<name>-hook.mp4 + hooks/CAPTIONS-HOOKS.md
"""
import json, os, subprocess
HERE = os.path.dirname(os.path.abspath(__file__)); V = os.path.join(HERE, "..")
HOOKS = {  # Video: (Hook Zeile 1, Zeile 2, Beschreibung)
 "french-basics-long": ("15 French words every beginner NEEDS 🇫🇷", "Can you say all 15? 👀",
   "15 French words every beginner needs 🇫🇷🐥 Save this and practice daily! Follow for Part 2 👇\n\n#learnfrench #frenchforbeginners #frenchvocabulary #languagelearning #learnwithcoco"),
 "french-part2": ("15 MORE French words 🇫🇷 PART 2", "Did you see Part 1? 👀",
   "French for beginners – Part 2 🇫🇷🐥 15 new everyday words! Follow so you don't miss Part 3 👇\n\n#learnfrench #frenchforbeginners #frenchvocabulary #languagelearning #learnwithcoco"),
 "japanese-basics": ("Learn 15 Japanese words in 60 seconds 🇯🇵", "#12 is so cute 🥹",
   "Your first 15 Japanese words 🇯🇵🐥 Which one is your favorite? Follow to learn Japanese step by step 👇\n\n#learnjapanese #japaneseforbeginners #japanesewords #languagelearning #learnwithcoco"),
 "japanese-part2": ("15 MORE Japanese words 🇯🇵 PART 2", "You'll use #15 every day 😋",
   "Japanese for beginners – Part 2 🇯🇵🐥 From \"ohayō\" to \"oishii\"! Follow for Part 3 👇\n\n#learnjapanese #japaneseforbeginners #japanesewords #languagelearning #learnwithcoco"),
 "korean-basics": ("Learn 15 Korean words in 60 seconds 🇰🇷", "K-drama fans know #12 💕",
   "Your first 15 Korean words 🇰🇷🐥 K-drama fans, how many did you know? Follow for Part 2 👇\n\n#learnkorean #koreanforbeginners #koreanwords #kdrama #learnwithcoco"),
 "false-friends-spanish": ("Most English speakers get #1 WRONG 😳🇪🇸", "12 Spanish words that TRICK you",
   "12 Spanish words that trick English speakers 😳🇪🇸 Which one fooled you? Follow for more 👇\n\n#learnspanish #spanishwords #falsefriends #languagelearning #learnwithcoco"),
 "spanish-basics": ("15 Spanish words you NEED 🇪🇸", "Can you say all 15? 👀",
   "Your first 15 Spanish words 🇪🇸🐥 How many did you know? Follow for Part 2 👇\n\n#learnspanish #spanishforbeginners #spanishvocabulary #languagelearning #learnwithcoco"),
 "italian-basics": ("15 Italian words you NEED 🇮🇹", "#12 is so romantic 💕",
   "Your first 15 Italian words 🇮🇹🐥 Which one is your favorite? Follow for Part 2 👇\n\n#learnitalian #italianforbeginners #italianvocabulary #languagelearning #learnwithcoco"),
}
jobs = [dict(out=os.path.join(HERE, f"_{n}.png"), kind="hook", l1=h[0], l2=h[1]) for n, h in HOOKS.items()]
jf = os.path.join(HERE, "_jobs.json"); json.dump(jobs, open(jf, "w"), ensure_ascii=False)
subprocess.run(["node", os.path.join(V, "clips", "overlay.mjs"), jf], check=True); os.remove(jf)
caps = ["# Hook-Versionen: Beschreibungen zum Kopieren\n"]
for name, (l1, l2, cap) in HOOKS.items():
    tl = json.load(open(os.path.join(V, name, "timeline.json")))
    src = os.path.join(V, name, "out", f"{name}-stimme.mp4"); out = os.path.join(HERE, f"{name}-hook.mp4")
    start = tl["intro"] - 0.05; dur = tl["duration"] - start
    fc = "[1:v]format=rgba,fade=t=out:st=4.6:d=0.4:alpha=1[h];[0:v][h]overlay=0:0:enable='lt(t,5)'[v]"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{start:.2f}", "-i", src, "-loop", "1", "-t", "5", "-i", os.path.join(HERE, f"_{name}.png"),
                    "-filter_complex", fc, "-map", "[v]", "-map", "0:a", "-t", f"{dur:.2f}", "-c:v", "libx264", "-preset", "medium", "-crf", "20",
                    "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-movflags", "+faststart", out], check=True)
    caps.append(f"\n**{name}-hook.mp4** ({dur:.1f} s)\n```\n{cap}\n```\n")
    print("hook", name, round(dur, 1), "s")
open(os.path.join(HERE, "CAPTIONS-HOOKS.md"), "w").write("".join(caps))
