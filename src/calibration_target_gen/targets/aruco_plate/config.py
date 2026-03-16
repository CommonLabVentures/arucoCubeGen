from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ArucoPlateConfig:
    plate_width_mm: float = 83.0
    plate_height_mm: float = 220.0
    plate_thickness_mm: float = 4.0

    marker_id: int = 0
    marker_size_mm: float | None = None

    aruco_dict_name: str = "DICT_4X4_50"
    aruco_marker_bits: int = 4
    aruco_border_bits: int = 1
    aruco_image_size: int = 240

    black_inlay_depth_mm: float = 0.8
    preview_long_side_px: int = 2200
    output_prefix: str = "out_aruco_plate"
