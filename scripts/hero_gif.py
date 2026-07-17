#!/usr/bin/env python3
"""Regenerate the animated README hero (docs/img/hero.gif).

Tells the attack->defense story on the Backdoor lesson:
  lesson -> Run attack (100% success) -> apply fine-pruning (0.9) -> success rate drops.

Requirements:
  - The app running at $APP_URL (default http://localhost:5173) — e.g. `docker compose up`.
  - `pip install playwright pillow` and a local Google Chrome (used via channel="chrome").

Usage:
  python scripts/hero_gif.py
"""
import os
import re
import io
import pathlib
from playwright.sync_api import sync_playwright
from PIL import Image

URL = os.environ.get("APP_URL", "http://localhost:5173")
OUT = pathlib.Path(__file__).resolve().parent.parent / "docs" / "img"
OUT.mkdir(parents=True, exist_ok=True)


def cap(pg):
    return Image.open(io.BytesIO(pg.screenshot())).convert("RGB")


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=True)
        pg = browser.new_page(viewport={"width": 1280, "height": 860}, device_scale_factor=1)
        pg.goto(URL, wait_until="networkidle")

        if pg.evaluate("() => document.documentElement.getAttribute('data-theme')") == "dark":
            pg.get_by_role("button", name=re.compile("theme", re.I)).click()
            pg.wait_for_timeout(400)

        # bump fine-pruning fraction 0.7 -> 0.9 via keyboard (React ignores JS .value writes)
        prune = pg.locator("input[type=range]").nth(1)
        prune.focus()
        for _ in range(4):
            prune.press("ArrowRight")
        pg.wait_for_timeout(200)

        f_intro = cap(pg)                                     # lesson, no result yet

        pg.get_by_role("button", name=re.compile("Run", re.I)).click()   # ATTACK
        pg.wait_for_selector("text=Attack success rate", timeout=25000)
        pg.wait_for_timeout(600)
        f_attack = cap(pg)                                    # ~100% success

        pg.get_by_role("checkbox").check()                    # apply defense
        pg.wait_for_timeout(300)
        f_check = cap(pg)

        pg.get_by_role("button", name=re.compile("Run", re.I)).click()   # DEFEND
        # wait on a phrase unique to the defended narrative (NOT "Fine-pruning",
        # which also appears in the always-present knob label)
        pg.wait_for_selector("text=/dormant channels/", timeout=60000)
        pg.wait_for_timeout(800)
        f_def = cap(pg)                                       # success rate dropped

        browser.close()

    # story loop with per-frame holds (ms)
    seq = [(f_intro, 1200), (f_attack, 2200), (f_check, 700), (f_def, 2600)]
    width = 1040
    imgs = [im.resize((width, round(im.height * width / im.width)), Image.LANCZOS) for im, _ in seq]
    imgs = [im.quantize(colors=200, method=Image.MEDIANCUT) for im in imgs]
    durs = [d for _, d in seq]
    imgs[0].save(OUT / "hero.gif", save_all=True, append_images=imgs[1:],
                 duration=durs, loop=0, optimize=True, disposal=2)
    print("wrote", OUT / "hero.gif", imgs[0].size)


if __name__ == "__main__":
    main()
