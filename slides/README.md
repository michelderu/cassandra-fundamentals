# Presentation deck

`cassandra-data-labs.pptx` is the slide deck for the four sessions. It follows the same clock as [`sessions/`](../sessions/README.md): explanation, then the lab, with the course posters full-screen where they already teach the idea.

Speaker notes are the instructor cues (what to say, what to cut if you are behind, where the full command lives).

## Open it as Google Slides

This repo cannot create the file in a Google account. Google Slides imports the PowerPoint as a native deck:

1. Go to [Google Slides](https://slides.google.com) → **Blank presentation**, or open [Google Drive](https://drive.google.com).
2. **File → Import slides → Upload** and choose `slides/cassandra-data-labs.pptx`.
   Or upload the file to Drive, then right-click → **Open with → Google Slides**.
3. **File → Save as Google Slides** so you have a Slides file you can share and present, not only a preview of the PowerPoint.
4. Present with speaker notes on (**Presenter view**). The notes come across with the import.

## Rebuild

```bash
pip install python-pptx pillow
python3 slides/build_deck.py
```

The script writes `slides/cassandra-data-labs.pptx`. Posters are read from [`assets/`](../assets) and scaled down into the file.
