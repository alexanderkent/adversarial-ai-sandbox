import re
import unicodedata

ZWSP = "​"
TECHNIQUES = ["homoglyph", "zero_width", "spacing", "leetspeak", "synonym", "reverse", "foreign"]

# ASCII -> visually-confusable Cyrillic/Greek letters.
HOMOGLYPHS = {
    "a": "а", "c": "с", "e": "е", "i": "і", "o": "о",
    "p": "р", "s": "ѕ", "x": "х", "y": "у",
}
_HOMO_REVERSE = {v: k for k, v in HOMOGLYPHS.items()}

# Trigger word -> meaning-preserving synonym. Targets are chosen to be OUT of the
# detector's training vocabulary (no character overlap to fold back), so a synonym
# swap both evades detection and survives normalization — the honest limitation.
SYNONYMS = {
    "ignore": "overlook", "previous": "foregoing", "instructions": "briefing",
    "reveal": "divulge", "system": "platform", "prompt": "preamble",
    "override": "supersede", "guidelines": "norms", "confidential": "privileged",
    "password": "passcode", "disregard": "dismiss", "restrictions": "limits",
}

# English -> French translation. Targets are chosen OUT of the detector's English
# training vocabulary (and never identical in spelling, e.g. NOT "instructions" ->
# "instructions"), so a translation both evades detection and survives normalization.
FOREIGN = {
    "ignore": "oublier", "previous": "précédentes", "instructions": "consignes",
    "reveal": "révélez", "system": "système", "prompt": "amorce",
    "override": "remplacez", "guidelines": "directives", "confidential": "confidentiel",
    "password": "motdepasse", "disregard": "négligez", "restrictions": "limites",
    "data": "données",
}

# ASCII letter -> leetspeak digit. Reversible: a leet digit inside an alphanumeric
# run that also contains letters folds back to its letter; a pure-number run is left
# alone (so "2024" is not mangled).
LEET = {"a": "4", "e": "3", "i": "1", "o": "0", "s": "5", "t": "7"}
_LEET_REVERSE = {v: k for k, v in LEET.items()}

_TOKEN_RE = re.compile(r"[A-Za-z]+|[^A-Za-z]+")  # alpha runs and non-alpha runs, in order


def _tokens(text: str) -> list[str]:
    return _TOKEN_RE.findall(text)


def _eligible(tok: str, technique: str) -> bool:
    if technique == "synonym":
        return tok.lower() in SYNONYMS
    if technique == "foreign":
        return tok.lower() in FOREIGN
    return tok.isalpha() and len(tok) >= 4


def _apply(tok: str, technique: str) -> str:
    if technique == "homoglyph":
        return "".join(HOMOGLYPHS.get(c, c) for c in tok)
    if technique == "zero_width":
        return ZWSP.join(tok)
    if technique == "spacing":
        return ".".join(tok)
    if technique == "leetspeak":
        return "".join(LEET.get(c, c) for c in tok)
    if technique == "synonym":
        return SYNONYMS[tok.lower()]
    if technique == "reverse":
        return tok[::-1]
    if technique == "foreign":
        return FOREIGN[tok.lower()]
    return tok


def _unleet(text: str) -> str:
    """Fold leetspeak digits back to letters, but only inside alphanumeric runs that
    contain at least one letter (a pure-number run like "2024" is left untouched)."""
    def fold(m):
        run = m.group(0)
        if any(ch.isalpha() for ch in run):
            return "".join(_LEET_REVERSE.get(ch, ch) for ch in run)
        return run
    return re.sub(r"[A-Za-z0-9]+", fold, text)


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
    filter). Cannot undo synonym swaps — that is the honest limitation of the defense.

    The homoglyph fold and dot-collapse are heuristics that assume ASCII-intended input:
    on genuinely non-ASCII text (e.g. real Cyrillic) they would over-normalize. That is
    fine for this teaching module, whose inputs are the fixed ASCII PAYLOADS."""
    text = text.replace(ZWSP, "")
    text = "".join(_HOMO_REVERSE.get(c, c) for c in text)
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r"(?<=[A-Za-z])\.(?=[A-Za-z])", "", text)  # undo "i.g.n.o.r.e"
    text = _unleet(text)                                # undo "1gn0r3" leetspeak
    return text
