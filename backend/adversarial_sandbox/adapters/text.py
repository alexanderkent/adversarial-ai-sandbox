import re
import unicodedata

ZWSP = "​"
TECHNIQUES = ["homoglyph", "zero_width", "spacing", "synonym"]

# ASCII -> visually-confusable Cyrillic/Greek letters.
HOMOGLYPHS = {
    "a": "а", "c": "с", "e": "е", "i": "і", "o": "о",
    "p": "р", "s": "ѕ", "x": "х", "y": "у",
}
_HOMO_REVERSE = {v: k for k, v in HOMOGLYPHS.items()}

# Trigger word -> meaning-preserving synonym (no character overlap to fold back).
SYNONYMS = {
    "ignore": "disregard", "instructions": "directives", "previous": "prior",
    "reveal": "disclose", "system": "config", "prompt": "preamble",
    "override": "supersede", "password": "passphrase", "confidential": "private",
    "disregard": "overlook",
}

_TOKEN_RE = re.compile(r"[A-Za-z]+|[^A-Za-z]+")  # alpha runs and non-alpha runs, in order


def _tokens(text: str) -> list[str]:
    return _TOKEN_RE.findall(text)


def _eligible(tok: str, technique: str) -> bool:
    if technique == "synonym":
        return tok.lower() in SYNONYMS
    return tok.isalpha() and len(tok) >= 4


def _apply(tok: str, technique: str) -> str:
    if technique == "homoglyph":
        return "".join(HOMOGLYPHS.get(c, c) for c in tok)
    if technique == "zero_width":
        return ZWSP.join(tok)
    if technique == "spacing":
        return ".".join(tok)
    if technique == "synonym":
        return SYNONYMS[tok.lower()]
    return tok


def perturb(text: str, technique: str, intensity: float) -> list[tuple[str, bool]]:
    """Return the text as (span_text, changed) tuples. `intensity` (0..1) is the
    fraction of eligible tokens (deterministically the first k) that get perturbed."""
    toks = _tokens(text)
    eligible = [i for i, t in enumerate(toks) if _eligible(t, technique)]
    k = round(intensity * len(eligible))
    chosen = set(eligible[:k])
    spans: list[tuple[str, bool]] = []
    for i, t in enumerate(toks):
        if i in chosen:
            new = _apply(t, technique)
            spans.append((new, new != t))
        else:
            spans.append((t, False))
    return spans


def normalize_text(text: str) -> str:
    """Fold away homoglyph / zero-width / spacing perturbations (a heuristic input
    filter). Cannot undo synonym swaps — that is the honest limitation of the defense."""
    text = text.replace(ZWSP, "")
    text = "".join(_HOMO_REVERSE.get(c, c) for c in text)
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r"(?<=[A-Za-z])\.(?=[A-Za-z])", "", text)  # undo "i.g.n.o.r.e"
    return text
