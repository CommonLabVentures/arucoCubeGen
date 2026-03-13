from __future__ import annotations

from dataclasses import dataclass, field

from src.aruco_cube_gen.config import Config as LegacyCubeConfig


@dataclass(frozen=True)
class CubeTargetConfig:
    legacy: LegacyCubeConfig = field(default_factory=LegacyCubeConfig)
