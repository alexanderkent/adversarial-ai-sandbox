"""Dev-time empirical check for the text-evasion demo (pure sklearn, deterministic).
Gate: every char technique must LOWER the injection score (evasion) and normalization
must RAISE it back (defense); synonym must evade AND survive normalization (honest limit)."""
from adversarial_sandbox.attacks.text_evasion import TextEvasion, PAYLOADS
from adversarial_sandbox.adapters import text as txt

m = TextEvasion()


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
            if tech == "synonym" and restored:
                ok = False  # synonym should NOT be restorable
            if tech != "synonym" and not restored:
                ok = False  # char techniques should be restorable
    print("\nGATE:", "PASS" if ok else "NEEDS ATTENTION")


if __name__ == "__main__":
    main()
