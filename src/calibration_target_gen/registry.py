from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from .targets.base import BaseTarget


def _build_cube_target() -> BaseTarget:
    from .targets.cube.adapter import CubeTarget

    return CubeTarget()


def _build_charuco_plate_target() -> BaseTarget:
    from .targets.charuco_plate.adapter import CharucoPlateTarget

    return CharucoPlateTarget()


def _build_aruco_plate_target() -> BaseTarget:
    from .targets.aruco_plate.adapter import ArucoPlateTarget

    return ArucoPlateTarget()


def _build_aruco_a4_sheet_target() -> BaseTarget:
    from .targets.aruco_a4_sheet.adapter import ArucoA4SheetTarget

    return ArucoA4SheetTarget()


@dataclass(frozen=True)
class RegisteredTarget:
    name: str
    description: str
    factory: Callable[[], BaseTarget]


_TARGETS: dict[str, RegisteredTarget] = {
    "aruco_a4_sheet": RegisteredTarget(
        name="aruco_a4_sheet",
        description="Multi-page printable A4 ArUco marker sheets with a centered 150 mm marker and 10 mm grid.",
        factory=_build_aruco_a4_sheet_target,
    ),
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
    "charuco_plate": RegisteredTarget(
        name="charuco_plate",
        description="Square 3x3 ChArUco plate with separate white and black AMS-ready STL bodies.",
        factory=_build_charuco_plate_target,
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
