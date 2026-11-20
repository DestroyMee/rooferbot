"""Stellt alle Videos für YouTube zusammen: nummerierte Dateien (ZIPs) + YOUTUBE.md mit Titel, Beschreibung, Tags.
Nutzung: python3 make_youtube.py <zielordner-für-zips>"""
import json, os, shutil, subprocess, sys
V = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = sys.argv[1]
CH = "@Learnwithcoco6767"
TAGS = "#learnlanguages #languagelearning #shorts"


def words(name, field="fr", en="en"):
    tl = json.load(open(os.path.join(V, name, "timeline.json")))
    return [(w.get(field) or w.get("es") or w.get("w"), w.get(en) or w.get("real") or w.get("lit")) for w in tl["words"]]


def basics(lang, flag, name, part, hook):
    ws = words(name)
    t = f"Learn 15 {lang} Words in 60 Seconds {flag}" + (f" (Part {part})" if part > 1 else "") + " #Shorts"
    d = (f"Learn your {'first' if part == 1 else 'next'} 15 {lang} words with Coco 🐥 – with pronunciation and English translation!\n"
         f"Watch, listen and repeat. Save this video and practice every day 📌\n\n"
         + "\n".join(f"• {a} = {b}" for a, b in ws) +
         f"\n\nSubscribe for Part {part + 1}! 🔔 {CH}\n\n#learn{lang.lower()} #{lang.lower()}forbeginners {TAGS}")
    src = f"hooks/{name}-hook.mp4" if hook else f"{name}/out/{name}-stimme.mp4"
    return src, t, d


def spicy(name, title, intro, tag):
    tl = json.load(open(os.path.join(V, name, "timeline.json")))
    lst = "\n".join(f"• {w['es']} = {w['en']}" for w in tl["words"])
    d = f"{intro}\nWhich one is your favorite? 😂 Comment below!\n⚠️ Not for kids – contains curse words (English censored).\n\n{lst}\n\nSubscribe for more 🌶️ {CH}\n\n{tag} {TAGS}"
    return f"{name}/out/{name}-stimme.mp4", title + " #Shorts", d


L = []
L.append(basics("Japanese", "🇯🇵", "japanese-basics", 1, True))
L.append(basics("French", "🇫🇷", "french-basics-long", 1, True))
ff = json.load(open(os.path.join(V, "false-friends-spanish", "timeline.json")))
L.append(("hooks/false-friends-spanish-hook.mp4", "12 Spanish Words That TRICK English Speakers 😳🇪🇸 #Shorts",
          "Spanish false friends: words that look like English but mean something totally different! 😂\nWhich one fooled you? Comment below!\n\n"
          + "\n".join(f"• {w['w']} ≠ {w['trap']} → {w['real']}" for w in ff["words"]) + f"\n\nSubscribe for more 🔔 {CH}\n\n#learnspanish #falsefriends {TAGS}"))
L.append(basics("Korean", "🇰🇷", "korean-basics", 1, True))
L.append(basics("Spanish", "🇪🇸", "spanish-basics", 1, True))
L.append(basics("Italian", "🇮🇹", "italian-basics", 1, True))
L.append(basics("Polish", "🇵🇱", "polish-basics", 1, False))
L.append(basics("Japanese", "🇯🇵", "japanese-part2", 2, True))
L.append(basics("French", "🇫🇷", "french-part2", 2, True))
for lang, flag, n in [("Spanish", "🇪🇸", "spanish-part2"), ("Italian", "🇮🇹", "italian-part2"), ("Polish", "🇵🇱", "polish-part2"), ("Korean", "🇰🇷", "korean-part2")]:
    L.append(basics(lang, flag, n, 2, False))
kg = json.load(open(os.path.join(V, "konglish", "timeline.json")))
L.append(("konglish/out/konglish-stimme.mp4", "English Words Koreans Use… DIFFERENTLY 😂🇰🇷 Konglish #Shorts",
          "Konglish: English words Koreans use in their own way! 📱 A cell phone is a \"hand phone\"!\nWhich one surprised you? Comment below!\n\n"
          + "\n".join(f"• {w['en']} = {w['ko']} ({w['rom']}) – literally \"{w['lit']}\"" for w in kg["words"]) + f"\n\nSubscribe for more 🔔 {CH}\n\n#learnkorean #konglish {TAGS}"))
dl = json.load(open(os.path.join(V, "dutch-literal", "timeline.json")))
L.append(("dutch-literal/out/dutch-literal-stimme.mp4", "Dutch Is Just English With Extra Steps 😂🇳🇱 #Shorts",
          "Dutch words translated literally are hilarious! A leopard is a \"lazy horse\" 🐆😴\nWhich one made you laugh? Comment below!\n\n"
          + "\n".join(f"• {w['w']} = {w['a']} + {w['b']} = {w['real']}" for w in dl["words"]) + f"\n\nSubscribe for more 🔔 {CH}\n\n#learndutch #dutchlanguage {TAGS}"))
L.append(spicy("spanish-spicy", "Spanish Curse Words They DON'T Teach You in School 🌶️🇪🇸", "Spanish curse words – Spain vs Latin America! 🌶️", "#learnspanish #spanishslang"))
L.append(spicy("spicy-spanish-2", "Mexican Slang They DON'T Teach You in School 🌶️🇲🇽", "Mexican slang you'll hear every day! From \"¡Chale!\" to \"¡No mames!\" 🌶️", "#learnspanish #mexicanslang"))
L.append(spicy("spicy-french", "French Curse Words They DON'T Teach You in School 🌶️🇫🇷", "French curse words – plus the polite versions 😇", "#learnfrench #frenchslang"))
L.append(spicy("spicy-italian", "Italian Curse Words They DON'T Teach You in School 🌶️🇮🇹", "Italian curse words – \"Che palle\" literally means \"what balls\" 😅", "#learnitalian #italianslang"))
L.append(spicy("spicy-portuguese", "Brazilian Curse Words They DON'T Teach You in School 🌶️🇧🇷", "Brazilian Portuguese curse words – you'll hear \"Nossa!\" every 5 minutes 😂", "#learnportuguese #brazilianportuguese"))
st = json.load(open(os.path.join(V, "french-story", "timeline.json")))
txt = lambda ps: "".join(p[0] if isinstance(p, list) else p for p in ps)
L.append(("french-story/out/french-story-stimme.mp4", "Ordering a Croissant in French 🥐🇫🇷 Learn With a Story #Shorts",
          "Learn real French phrases with a little story at the bakery – and take the quiz at the end! 🥐\n\n"
          + "\n".join(f"• {txt(l['fr'])} = {txt(l['en'])}" for l in st["lines"]) + f"\n\nSubscribe for more stories 🔔 {CH}\n\n#learnfrench #frenchlesson {TAGS}"))
nm = json.load(open(os.path.join(V, "french-numbers", "timeline.json")))
L.append(("french-numbers/out/french-numbers-stimme.mp4", "Count to 15 in French 🇫🇷🎈 French Numbers for Beginners #Shorts",
          "Learn French numbers 1–15 with Coco! Count the balloons and repeat 🎈\n\n" + "\n".join(f"• {w['n']} = {w['fr']}" for w in nm["words"])
          + f"\n\nSubscribe for more 🔔 {CH}\n\n#learnfrench #frenchnumbers {TAGS}"))

os.makedirs(OUT, exist_ok=True)
md = ["# YouTube-Upload: alle Videos für " + CH, "",
      "**Bei JEDEM Video in YouTube Studio:**",
      "- Zielgruppe: **„Nein, nicht speziell für Kinder“** (sonst keine Kommentare und weniger Werbeeinnahmen)",
      "- Titel und Beschreibung unten einfach kopieren. #Shorts im Titel sorgt dafür, dass es als Short läuft.",
      "- Reihenfolge: einfach von 01 aufwärts, 1–2 Videos pro Tag.", ""]
missing = []
for i, (src, t, d) in enumerate(L, 1):
    fn = f"{i:02d}-{os.path.basename(os.path.dirname(os.path.dirname(src))) if '/out/' in src else os.path.basename(src)[:-9]}.mp4"
    p = os.path.join(V, src)
    if os.path.exists(p): shutil.copy(p, os.path.join(OUT, fn))
    else: missing.append(fn)
    md += [f"## {fn}", "", "**Titel:**", "```", t, "```", "**Beschreibung:**", "```", d, "```", ""]
open(os.path.join(V, "youtube", "YOUTUBE.md"), "w").write("\n".join(md))
print(len(L), "Videos;", "fehlen noch:", missing)
