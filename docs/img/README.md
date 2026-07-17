# Screenshots

The top-level README references these images:

- `hero.gif` — the animated README hero (plant a backdoor, then apply the defense).
- `hero.png` — static version of the hero; use it as the GitHub **social-preview** image
  (Settings → General → Social preview), since previews don't animate GIFs.
- `dark.png` — the app in dark theme, scrolled to the footer.
- `atlas.png` — the MITRE ATLAS coverage matrix.

Capture at a desktop width (~1280px) for a crisp hero. A short GIF of running an attack and
toggling its defense makes the best social/README asset.

## Regenerating

These are produced by scripts (run the app first, e.g. `docker compose up`):

```bash
pip install -e "./backend[screenshots]"   # playwright + pillow; uses local Chrome
python scripts/screenshots.py              # hero.png, dark.png, atlas.png
python scripts/hero_gif.py                 # hero.gif (attack -> defense story)
```

(Run the scripts from the repo root; they write into `docs/img/`.)

