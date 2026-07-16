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

from .schema import AtlasMatrix, AtlasColumn, AtlasCell, AtlasAttackRef


def build_matrix(modules) -> AtlasMatrix:
    # Aggregate covered techniques across modules, remembering first-seen order.
    defs: dict[str, AtlasTechnique] = {}
    refs: dict[str, list[AtlasAttackRef]] = {}
    order: list[str] = []
    for m in modules:
        d = m.describe()
        for t in d.atlas:
            if t.id not in defs:
                defs[t.id] = t
                refs[t.id] = []
                order.append(t.id)
            refs[t.id].append(AtlasAttackRef(attack_id=d.id, attack_name=d.name))

    columns: list[AtlasColumn] = []
    for tactic in TACTICS:
        cells: list[AtlasCell] = []
        for tid in order:                      # covered-first, registration order
            t = defs[tid]
            if t.tactic == tactic:
                cells.append(AtlasCell(id=t.id, name=t.name, url=t.url, covered=True,
                                       subtechniques=t.subtechniques, attacks=refs[tid]))
        for t in CONTEXT_TECHNIQUES:           # then greyed context
            if t.tactic == tactic:
                cells.append(AtlasCell(id=t.id, name=t.name, url=t.url, covered=False,
                                       subtechniques=t.subtechniques, attacks=[]))
        columns.append(AtlasColumn(tactic=tactic, cells=cells))
    return AtlasMatrix(tactics=columns)
