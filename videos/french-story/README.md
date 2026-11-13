# Reel: „À la boulangerie“ – Learn French with Stories, Folge 1

Dialog-Geschichte im Bilderbuch-Stil (1080×1920, 30 fps, 42 s). Coco, ein Küken mit Baskenmütze, kauft bei
Madame Minou, einer Bäcker-Katze, ein Croissant. Französisch steht in der Sprechblase, Englisch darunter.
**Zusammengehörige Wörter haben in beiden Sprachen dieselbe Farbe.** Danach kommt ein Quiz mit 3-2-1-Countdown und
zum Schluss eine Aufforderung zum Kommentieren.

| Datei | Inhalt |
|---|---|
| `out/french-story.mp4` | fertiges Video mit Akkordeon-Walzer und Effekten, **ohne Stimmen** |
| `sprechertext.srt` | Sprechertext mit Zeitmarken und Rollen (Coco, Madame Minou, Erzähler) |
| `timeline.json` | **Dialog und Quiz**: Sätze, Farb-Markierungen (Zahl 1–6) und Quiz-Antworten |
| `scene.html` | Zeichnungen (SVG), Kamerafahrten, Animation |

Neue Folge: Dialog und Quiz in `timeline.json` ändern. Die Bäckerei-Szene bleibt gleich.
Für einen neuen Ort, zum Beispiel ein Café, muss in `scene.html` die Funktion `world()` angepasst werden.

```bash
node render.mjs && python3 audio.py
ffmpeg -i out/frames.mp4 -i out/music_sfx.wav -c:v copy -c:a aac -b:a 192k -shortest out/french-story.mp4
```

**Stimmen:** Coco und Madame Minou sprechen Französisch (am besten mit einer französischen Stimme),
der Erzähler spricht Englisch. Zwei verschiedene Stimmen für die Figuren machen die Geschichte lebendiger.
