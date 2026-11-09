# Reel: „Dein Nachbar hat einen Baum“

Hochkant-Video (1080×1920, 30 fps, 36,5 s) im Stil eines Erklärvideos mit einfacher 3D-Grafik.
Markenzeichen ist der Querschnitt durchs Dach: Ziegel, Lattung, Folie, Dämmung.

## Dateien

| Datei | Inhalt |
|---|---|
| `out/nachbar-baum.mp4` | fertiges Video mit Musik und Soundeffekten, **ohne Sprecher** |
| `sprechertext.srt` | Sprechertext mit Zeitmarken zum Einsprechen |
| `timeline.json` | Sätze und Zeiten (steuert die Einzelwort-Untertitel) |
| `scene.html` | 3D-Szene (three.js), alle Animationen hängen nur von der Zeit `t` ab |
| `render.mjs` | rendert die Szene Bild für Bild mit Playwright + ffmpeg |
| `audio.py` | erzeugt Musik und Soundeffekte (numpy) |

## Stimme einsprechen (CapCut)

1. `nachbar-baum.mp4` in CapCut importieren.
2. Auf **Voiceover** tippen und den Text aus `sprechertext.srt` einsprechen.
   Jeder Satz beginnt an seiner Zeitmarke. Die Untertitel zeigen dir das Tempo.
3. Musik-Spur leiser stellen, falls die Stimme untergeht.
4. In der Videobeschreibung `@DEIN.DACH.ACCOUNT` durch deinen Namen ersetzen,
   oder den Text in `scene.html` (id `handle`) ändern und neu rendern.

## Neu rendern

```bash
npm i playwright        # falls nicht vorhanden; Chromium wird benötigt
node render.mjs --stills 2,8,20   # Vorschaubilder in out/
node render.mjs                   # out/frames.mp4
python3 audio.py                  # out/music_sfx.wav
ffmpeg -i out/frames.mp4 -i out/music_sfx.wav -c:v copy -c:a aac -b:a 192k -shortest out/nachbar-baum.mp4
```

Texte oder Zeiten ändern: `timeline.json` anpassen. Die Untertitel richten sich automatisch danach.
Animationen hängen an festen Zeitpunkten in `scene.html` → `window.render(t)`.

## Rechtlicher Hinweis zum Inhalt

Das Video vereinfacht § 910 BGB (Überhang). Ob und wann du Äste selbst kürzen darfst,
hängt vom Einzelfall und von Landesrecht ab. Im Zweifel vorher beraten lassen.
