# Screenshots

The top-level README references these images:

- `hero.gif` — the animated hero (plant a backdoor, then apply the defense).
- `hero.png` — Backdoor lesson, light theme, after *Run attack* (digit triptych + metrics).
- `dark.png` — same in dark theme, scrolled to the footer.
- `atlas.png` — the MITRE ATLAS coverage matrix.

Capture at a desktop width (~1280px) for a crisp hero. A short GIF of running an attack and
toggling its defense makes the best social/README asset.

## Regenerating

These are produced by scripts (run the app first, e.g. `docker compose up`):

```bash
pip install playwright pillow      # uses your local Chrome, no browser download
python scripts/screenshots.py      # hero.png, dark.png, atlas.png
python scripts/hero_gif.py         # hero.gif (attack -> defense story)
```

