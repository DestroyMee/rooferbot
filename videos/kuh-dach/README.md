# Reel: „Wie viele Kühe hält dein Dach aus?“

Absurdes Erklärvideo (1080×1920, 30 fps, 40 s): Kühe fallen vom Himmel aufs Dach, ein Zähler zeigt Anzahl und Gewicht.
Bei Kuh 13 (einer Riesenkuh mit Sonnenbrille) bricht das Haus zusammen. Dann wird zurückgespult und die Auflösung kommt:
30 cm nasser Schnee wiegen genauso viel wie 12 Kühe.

| Datei | Inhalt |
|---|---|
| `out/kuh-dach.mp4` | fertiges Video mit Polka-Musik und Soundeffekten, **ohne Sprecher** |
| `sprechertext.srt` | Sprechertext mit Zeitmarken |
| `timeline.json` | Sätze und Zeiten für die Einzelwort-Untertitel |
| `scene.html` | 3D-Szene (three.js) |
| `render.mjs` / `audio.py` | Bild rendern / Ton erzeugen |

Neu bauen:

```bash
node render.mjs && python3 audio.py
ffmpeg -i out/frames.mp4 -i out/music_sfx.wav -c:v copy -c:a aac -b:a 192k -shortest out/kuh-dach.mp4
```

## Die Rechnung im Video

- Dach-Schneelast: je nach Schneelastzone grob 70–110 kg/m², im Video gerundet auf **100 kg/m²**
- Dachfläche des Modellhauses: ca. 80 m² → **8 Tonnen**
- Kuh: ca. 650 kg → 8000 ÷ 650 ≈ **12 Kühe**
- Nasser Schnee: ca. 300–400 kg/m³ → 30 cm ≈ 100 kg/m²

Echte Dächer haben Sicherheitsreserven. Dass es bei Kuh 13 kracht, ist Show, keine Statik.
In den Videotext gehört deshalb ein Hinweis wie „vereinfacht, keine Statikberatung“.
