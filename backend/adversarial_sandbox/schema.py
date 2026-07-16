from typing import Literal, Any
from pydantic import BaseModel


class Knob(BaseModel):
    name: str
    label: str
    type: Literal["slider", "toggle", "select"]
    default: Any
    min: float | None = None
    max: float | None = None
    step: float | None = None
    options: list[str] | None = None
    help: str = ""


class SweepSpec(BaseModel):
    x_knob: str
    x_values: list[float]
    x_label: str
    y_label: str
    attacked_metric: str
    defended_metric: str | None = None


class Figure(BaseModel):
    kind: Literal["figure"] = "figure"
    png_base64: str
    caption: str = ""


class TranscriptTurn(BaseModel):
    role: Literal["system", "user", "document", "assistant"]
    content: str
    injected: bool = False


class Transcript(BaseModel):
    kind: Literal["transcript"] = "transcript"
    turns: list[TranscriptTurn]
    caption: str = ""


class TextSpan(BaseModel):
    text: str
    changed: bool = False


class TextVariant(BaseModel):
    label: str
    spans: list[TextSpan]
    score: float
    score_display: str


class TextComparison(BaseModel):
    kind: Literal["text_comparison"] = "text_comparison"
    variants: list[TextVariant]
    caption: str = ""


class CodeSnippet(BaseModel):
    label: str
    language: str = "python"
    source: str


class Metric(BaseModel):
    label: str
    value: float
    display: str


class DecisionDomain(BaseModel):
    x_min: float
    x_max: float
    y_min: float
    y_max: float


class DecisionPoint(BaseModel):
    x: float
    y: float
    label: int
    poison: bool = False


class DecisionState(BaseModel):
    title: str
    domain: DecisionDomain
    grid: list[list[int]]
    resolution: int
    points: list[DecisionPoint]
    accuracy: float


class DecisionSurface(BaseModel):
    kind: Literal["decision_surface"] = "decision_surface"
    states: list[DecisionState]
    caption: str = ""


class RunResult(BaseModel):
    figure: Figure | None = None
    metrics: list[Metric]
    narrative: str
    transcript: Transcript | None = None
    text_comparison: TextComparison | None = None
    decision_surface: DecisionSurface | None = None


class AtlasSubtechnique(BaseModel):
    id: str
    name: str


class AtlasTechnique(BaseModel):
    id: str
    name: str
    tactic: str
    url: str
    subtechniques: list[AtlasSubtechnique] = []


class AtlasAttackRef(BaseModel):
    attack_id: str
    attack_name: str


class AtlasCell(BaseModel):
    id: str
    name: str
    url: str
    covered: bool
    subtechniques: list[AtlasSubtechnique] = []
    attacks: list[AtlasAttackRef] = []


class AtlasColumn(BaseModel):
    tactic: str
    cells: list[AtlasCell]


class AtlasMatrix(BaseModel):
    tactics: list[AtlasColumn]


class AttackDescription(BaseModel):
    id: str
    name: str
    group: str
    summary: str
    formula: str
    threat_model: str
    knobs: list[Knob]
    has_defense: bool = True
    sweep: SweepSpec | None = None
    code: list[CodeSnippet] = []
    atlas: list[AtlasTechnique] = []


def validate_params(knobs: list[Knob], params: dict) -> dict:
    clean: dict[str, Any] = {}
    for knob in knobs:
        raw = params.get(knob.name, knob.default)
        if knob.type == "slider":
            val = float(raw)
            if knob.min is not None and val < knob.min:
                raise ValueError(f"{knob.name}={val} below min {knob.min}")
            if knob.max is not None and val > knob.max:
                raise ValueError(f"{knob.name}={val} above max {knob.max}")
        elif knob.type == "toggle":
            val = bool(raw)
        elif knob.type == "select":
            val = str(raw)
            if knob.options and val not in knob.options:
                raise ValueError(f"{knob.name}={val!r} not in {knob.options}")
        else:  # pragma: no cover - guarded by Literal
            raise ValueError(f"unknown knob type {knob.type}")
        clean[knob.name] = val
    return clean
