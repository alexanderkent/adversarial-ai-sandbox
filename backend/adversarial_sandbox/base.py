from abc import ABC, abstractmethod
from .schema import AttackDescription, RunResult, validate_params


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
