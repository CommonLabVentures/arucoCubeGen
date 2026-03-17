from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ArucoA4SheetConfig:
    page_width_mm: float = 210.0
    page_height_mm: float = 297.0
    marker_size_mm: float = 150.0

    marker_ids: tuple[int, ...] = tuple(range(16))

    aruco_dict_name: str = "DICT_4X4_50"
    aruco_marker_bits: int = 4
    aruco_border_bits: int = 1
    aruco_image_size: int = 240

    grid_spacing_mm: float = 10.0
    grid_line_width_mm: float = 0.2
    grid_gray: float = 0.82

    output_prefix: str = "out_aruco_a4_sheet"
