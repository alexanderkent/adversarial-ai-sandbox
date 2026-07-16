"""Curated MITRE ATLAS scaffold for the coverage matrix.

Tactic assignments below reflect atlas.mitre.org at build time; ATLAS is a
living framework, so re-verify when touching this file. Techniques that span
multiple tactics are placed in the single column that reads best for the
lesson matrix.
"""
from .schema import AtlasTechnique, AtlasSubtechnique


def technique(id: str, name: str, tactic: str,
              subtechniques: list[AtlasSubtechnique] | None = None) -> AtlasTechnique:
    return AtlasTechnique(
        id=id, name=name, tactic=tactic,
        url=f"https://atlas.mitre.org/techniques/{id}",
        subtechniques=subtechniques or [],
    )


# Curated tactic columns, in kill-chain order.
TACTICS: list[str] = [
    "Resource Development",
    "ML Model Access",
    "ML Attack Staging",
    "Defense Evasion",
    "Impact",
]

# Greyed, not-covered techniques shown for matrix realism.
CONTEXT_TECHNIQUES: list[AtlasTechnique] = [
    technique("AML.T0040", "ML Model Inference API Access", "ML Model Access"),
    technique("AML.T0031", "Erode ML Model Integrity", "Impact"),
]
