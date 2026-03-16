from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .targets.base import BaseTarget


def _build_cube_target() -> BaseTarget:
    from .targets.cube.adapter import CubeTarget

    return CubeTarget()


def _build_aruco_plate_target() -> BaseTarget:
    from .targets.aruco_plate.adapter import ArucoPlateTarget

    return ArucoPlateTarget()


@dataclass(frozen=True)
class RegisteredTarget:
    name: str
    description: str
    factory: Callable[[], BaseTarget]


_TARGETS: dict[str, RegisteredTarget] = {
    "aruco_plate": RegisteredTarget(
        name="aruco_plate",
        description="Rectangular single-marker ArUco plate with separate white and black AMS-ready STL bodies.",
        factory=_build_aruco_plate_target,
    ),
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
