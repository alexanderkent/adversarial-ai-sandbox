#!/usr/bin/env python3
"""Regenerate the animated README hero (docs/img/hero.gif).

A short guided tour of the sandbox in action:
  1. FGSM evasion  — run the attack, watch the digit get misclassified
  2. Backdoor sweep — the trade-off curve streams in live
  3. Data poisoning — morph the decision boundary clean <-> poisoned
  4. Prompt injection — a real local LLM gets hijacked into emitting HACKED
  5. MITRE ATLAS   — the coverage matrix

Requirements:
  - The app running at $APP_URL (default http://localhost:5173) with its backend on :8000
    (e.g. `docker compose up`, or uvicorn + `npm run dev`).
  - `pip install -e "./backend[screenshots]"` and a local Google Chrome (used via
    channel="chrome", so no extra browser download is needed).

Usage:
  python scripts/hero_gif.py
"""
import io
import os
import pathlib
import re
from playwright.sync_api import sync_playwright
from PIL import Image

URL = os.environ.get("APP_URL", "http://localhost:5173")
OUT = pathlib.Path(__file__).resolve().parent.parent / "docs" / "img"
OUT.mkdir(parents=True, exist_ok=True)

WIDTH = 960          # final GIF width in px
COLORS = 160         # palette size (size/quality trade-off)

frames: list[Image.Image] = []
durations: list[int] = []


def shot(pg, hold=140):
    """Capture one frame, displayed for `hold` ms."""
    frames.append(Image.open(io.BytesIO(pg.screenshot())).convert("RGB"))
    durations.append(hold)


def film(pg, seconds, fps=5, hold=140):
    """Capture frames for `seconds` while something animates on screen."""
    for _ in range(int(seconds * fps)):
        shot(pg, hold)
        pg.wait_for_timeout(int(1000 / fps))


def top(pg):
    """Scroll back to the top so every scene is framed the same way (clicking a Run
    button near the bottom of the form leaves the page scrolled)."""
    pg.evaluate("() => window.scrollTo(0, 0)")
    pg.wait_for_timeout(250)


def pick(pg, name):
    """Select a lesson from the sidebar."""
    pg.get_by_role("button", name=name).click()
    pg.wait_for_timeout(500)
    top(pg)


def scene_evasion(pg):
    pick(pg, "Adversarial Perturbation (FGSM/PGD)")
    shot(pg, 900)                                        # the lesson
    pg.get_by_role("button", name=re.compile("^Run", re.I)).click()
    film(pg, 1.2)                                        # running
    pg.wait_for_selector("text=Adversarial confidence", timeout=30000)
    top(pg)
    shot(pg, 2200)                                       # payoff: the digit flipped


def scene_sweep(pg):
    pick(pg, "Backdoor (BadNets trigger)")
    pg.get_by_role("tab", name="Sweep").click()
    pg.wait_for_timeout(400)
    shot(pg, 700)
    pg.get_by_role("button", name="Run sweep").click()
    # Each sweep point retrains a pruned model (~10s), so film one frame per completed
    # point rather than at a fixed fps — that is what makes the curve visibly build.
    counter = pg.locator("span").filter(has_text=re.compile(r"^\d+ / \d+$")).first
    seen, total = None, None
    for _ in range(300):                                 # up to ~150s
        pg.wait_for_timeout(500)
        try:
            label = counter.inner_text(timeout=1000).strip()
        except Exception:
            continue
        if label != seen:
            seen = label
            total = label.split("/")[-1].strip()
            shot(pg, 650)                                # a new point landed on the chart
        if seen == f"{total} / {total}":
            break
    pg.wait_for_timeout(700)
    shot(pg, 2600)                                       # payoff: defended vs attacked curve


def scene_poisoning(pg):
    pick(pg, "Data Poisoning")
    pg.get_by_role("button", name=re.compile("^Run", re.I)).click()
    pg.wait_for_selector('svg[aria-label="Decision boundary"]', timeout=30000)
    top(pg)
    pg.wait_for_timeout(400)
    shot(pg, 1400)
    states = pg.locator('div[role="group"][aria-label="Model state"] button')
    for i in range(states.count()):                      # morph clean <-> poisoned
        states.nth(i).click()
        pg.wait_for_timeout(450)
        shot(pg, 1500)


def scene_injection(pg):
    pick(pg, "Prompt Injection (direct & indirect)")
    shot(pg, 900)
    pg.get_by_role("button", name=re.compile("^Run", re.I)).click()
    film(pg, 2.0, fps=3)                                 # the local LLM thinks
    pg.wait_for_selector("text=Injection obeyed", timeout=120000)
    top(pg)
    pg.wait_for_timeout(400)
    shot(pg, 2600)                                       # payoff: hijacked transcript


def scene_atlas(pg):
    pg.get_by_role("button", name="MITRE ATLAS").click()
    pg.wait_for_selector("text=COVERAGE MATRIX", timeout=10000)
    pg.wait_for_timeout(500)
    shot(pg, 2800)


SCENES = [
    ("evasion", scene_evasion),
    ("sweep", scene_sweep),
    ("poisoning", scene_poisoning),
    ("injection", scene_injection),
    ("atlas", scene_atlas),
]


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=True)
        pg = browser.new_page(viewport={"width": 1280, "height": 860}, device_scale_factor=1)
        pg.goto(URL, wait_until="networkidle")

        if pg.evaluate("() => document.documentElement.getAttribute('data-theme')") == "dark":
            pg.get_by_role("button", name=re.compile("theme", re.I)).click()
            pg.wait_for_timeout(400)

        for name, scene in SCENES:
            scene(pg)
            print(f"  captured {name}: {len(frames)} frames so far")

        browser.close()

    imgs = [im.resize((WIDTH, round(im.height * WIDTH / im.width)), Image.LANCZOS) for im in frames]
    imgs = [im.quantize(colors=COLORS, method=Image.MEDIANCUT) for im in imgs]
    path = OUT / "hero.gif"
    imgs[0].save(path, save_all=True, append_images=imgs[1:], duration=durations,
                 loop=0, optimize=True, disposal=2)
    total = sum(durations) / 1000
    print(f"wrote {path}  {len(imgs)} frames  {imgs[0].size}  ~{total:.0f}s  "
          f"{path.stat().st_size / 1e6:.1f} MB")


if __name__ == "__main__":
    main()
