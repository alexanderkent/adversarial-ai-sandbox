"""Dev-time empirical check for the text-evasion demo (pure sklearn, deterministic).
Gate: every technique must LOWER the injection score (evasion). Foldable techniques
(homoglyph / zero_width / spacing / leetspeak) must be RESTORED by normalization;
non-foldable ones (synonym / reverse / foreign) must survive it (the honest limit)."""
from adversarial_sandbox.attacks.text_evasion import TextEvasion, PAYLOADS
from adversarial_sandbox.adapters import text as txt

m = TextEvasion()

FOLDABLE = {"homoglyph", "zero_width", "spacing", "leetspeak"}
NON_FOLDABLE = {"synonym", "reverse", "foreign"}


def main():
    ok = True
    for payload in PAYLOADS:
        for tech in txt.TECHNIQUES:
            r = m.run({"payload": payload, "technique": tech, "intensity": 1.0})
            d = m.defend({"payload": payload, "technique": tech, "intensity": 1.0})
            s_orig, s_pert = r.metrics[0].value, r.metrics[1].value
            s_norm = d.metrics[1].value
            evaded = s_pert < s_orig
            restored = s_norm > s_pert + 0.1
            print(f"{payload:14s} {tech:10s} orig={s_orig:.2f} pert={s_pert:.2f} "
                  f"norm={s_norm:.2f} evaded={evaded} restored={restored}")
            if not (s_orig > 0.5 and evaded):
                ok = False
            if tech in FOLDABLE and not restored:
                ok = False
            if tech in NON_FOLDABLE and restored:
                ok = False
    print("\nGATE:", "PASS" if ok else "NEEDS ATTENTION")


if __name__ == "__main__":
    main()
