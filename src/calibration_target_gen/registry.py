from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .targets.base import BaseTarget


def _build_cube_target() -> BaseTarget:
    from .targets.cube.adapter import CubeTarget

    return CubeTarget()


@dataclass(frozen=True)
class RegisteredTarget:
    name: str
    description: str
    factory: Callable[[], BaseTarget]


_TARGETS: dict[str, RegisteredTarget] = {
    "cube": RegisteredTarget(
        name="cube",
        description="Existing hollow cube plus marker plate outputs.",
        factory=_build_cube_target,
    ),
}


def get_target(name: str) -> BaseTarget:
    try:
        return _TARGETS[name].factory()
    except KeyError as exc:
        options = ", ".join(sorted(_TARGETS))
        raise SystemExit(f"Unknown target '{name}'. Available targets: {options}") from exc


def iter_targets() -> tuple[RegisteredTarget, ...]:
    return tuple(_TARGETS[name] for name in sorted(_TARGETS))
