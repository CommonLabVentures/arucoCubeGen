from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

from ..artifacts import Artifact


@dataclass(frozen=True)
class TargetRunResult:
    target_name: str
    output_dir: Path
    artifacts: tuple[Artifact, ...]


class BaseTarget(Protocol):
    name: str
    description: str

    def generate(self) -> TargetRunResult:
        ...
