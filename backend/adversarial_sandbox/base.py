from abc import ABC, abstractmethod
from typing import Iterator
from .schema import AttackDescription, RunResult, validate_params


def _metric_value(result: RunResult, label: str) -> float:
    for m in result.metrics:
        if m.label == label:
            return m.value
    raise ValueError(f"metric {label!r} not found in result")


class AttackModule(ABC):
    id: str = ""
    name: str = ""
    group: str = ""

    @abstractmethod
    def describe(self) -> AttackDescription: ...

    @abstractmethod
    def run(self, params: dict) -> RunResult: ...

    @abstractmethod
    def defend(self, params: dict) -> RunResult: ...

    def clean_params(self, params: dict) -> dict:
        return validate_params(self.describe().knobs, params)

    def sweep(self, params: dict) -> Iterator[dict]:
        spec = self.describe().sweep
        if spec is None:
            raise ValueError(f"attack {self.id!r} has no sweep spec")
        base = self.clean_params(params)
        for x in spec.x_values:
            p = {**base, spec.x_knob: x}
            try:
                point = {"x": x, "attacked": _metric_value(self.run(p), spec.attacked_metric)}
                if spec.defended_metric is not None:
                    point["defended"] = _metric_value(self.defend(p), spec.defended_metric)
            except (ValueError, FileNotFoundError) as e:
                point = {"x": x, "error": str(e)}
            yield point
