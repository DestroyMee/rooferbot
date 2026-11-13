# Reel: „French for Beginners“ (10 Grundwörter, Englisch übersetzt)

Kinder-Zeichentrick im Hochformat (1080×1920, 30 fps, 47 s). Maskottchen ist **Coco**, ein Küken mit Baskenmütze.
Pro Wort 4 Sekunden: Bild, französisches Wort, Aussprachehilfe, englische Übersetzung, „REPEAT!“.

| Datei | Inhalt |
|---|---|
| `out/french-basics.mp4` | fertiges Video mit Musik und Soundeffekten, **ohne Sprecher** |
| `sprechertext.srt` | Sprechertext mit Zeitmarken (Französisch → Englisch → Französisch wiederholen) |
| `timeline.json` | **Wortliste**: hier Wörter, Aussprache, Übersetzung, Bild und Farbe ändern |
| `scene.html` | Zeichnungen (SVG) und Animation |
| `render.mjs` / `audio.py` | Bild rendern / Ton erzeugen |

## Neue Folge machen

In `timeline.json` die Wörter austauschen. Vorhandene Bilder (`pic`): `sun`, `gift`, `yes`, `no`, `please`,
`bye`, `cat`, `dog`, `apple`, `water`. Für neue Wörter muss in `scene.html` unter `PICS` ein neues Bild ergänzt werden.

```bash
node render.mjs && python3 audio.py
ffmpeg -i out/frames.mp4 -i out/music_sfx.wav -c:v copy -c:a aac -b:a 192k -shortest out/french-basics.mp4
```

## Stimme

Bei einem Sprachvideo ist die **Aussprache das Wichtigste**. Die französischen Wörter sollten von einer
französischen Stimme kommen, zum Beispiel einer französischen Muttersprachlerin oder einem Muttersprachler oder einer KI-Stimme
mit französischem Akzent (z. B. ElevenLabs). Die englischen Teile kannst du selbst sprechen.
