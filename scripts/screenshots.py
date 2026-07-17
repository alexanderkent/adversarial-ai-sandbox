#!/usr/bin/env python3
"""Regenerate the README screenshots (docs/img/{hero,dark,atlas}.png).

Captures the running app headlessly at desktop width, 2x, as full-page PNGs.

Requirements:
  - The app running at $APP_URL (default http://localhost:5173) — e.g. `docker compose up`.
  - `pip install playwright` and a local Google Chrome (used via channel="chrome",
    so no extra browser download is needed).

Usage:
  python scripts/screenshots.py            # uses http://localhost:5173
  APP_URL=http://localhost:8080 python scripts/screenshots.py
"""
import os
import re
import pathlib
from playwright.sync_api import sync_playwright

URL = os.environ.get("APP_URL", "http://localhost:5173")
OUT = pathlib.Path(__file__).resolve().parent.parent / "docs" / "img"
OUT.mkdir(parents=True, exist_ok=True)


def set_theme(pg, want):
    if pg.evaluate("() => document.documentElement.getAttribute('data-theme')") != want:
        pg.get_by_role("button", name=re.compile("theme", re.I)).click()
        pg.wait_for_timeout(400)


def run_attack(pg):
    pg.get_by_role("button", name=re.compile("Run", re.I)).click()
    pg.wait_for_selector("text=Attack success rate", timeout=25000)
    pg.wait_for_timeout(700)


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(channel="chrome", headless=True)
        pg = browser.new_page(viewport={"width": 1280, "height": 820}, device_scale_factor=2)

        # hero — light, Backdoor lesson with a live result
        pg.goto(URL, wait_until="networkidle")
        set_theme(pg, "light")
        run_attack(pg)
        pg.screenshot(path=str(OUT / "hero.png"), full_page=True)
        print("wrote", OUT / "hero.png")

        # dark — same view
        set_theme(pg, "dark")
        run_attack(pg)
        pg.screenshot(path=str(OUT / "dark.png"), full_page=True)
        print("wrote", OUT / "dark.png")

        # atlas — MITRE ATLAS coverage matrix, light
        set_theme(pg, "light")
        pg.get_by_role("button", name="MITRE ATLAS").click()
        pg.wait_for_selector("text=COVERAGE MATRIX", timeout=10000)
        pg.wait_for_timeout(500)
        pg.screenshot(path=str(OUT / "atlas.png"), full_page=True)
        print("wrote", OUT / "atlas.png")

        browser.close()


if __name__ == "__main__":
    main()
