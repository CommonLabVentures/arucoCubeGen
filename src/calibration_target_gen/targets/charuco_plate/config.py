from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CharucoPlateConfig:
    plate_size_mm: float = 220.0
    plate_thickness_mm: float = 4.0

    board_squares_x: int = 3
    board_squares_y: int = 3
    board_margin_fraction: float = 0.88
    marker_length_fraction: float = 0.7
    top_left_square_black: bool = True

    aruco_dict_name: str = "DICT_4X4_50"
    aruco_marker_bits: int = 4
    aruco_border_bits: int = 1
    aruco_image_size: int = 240
    marker_ids: tuple[int, ...] = (0, 1, 2, 3)

    black_inlay_depth_mm: float = 0.8
    preview_image_size_px: int = 2200
    output_prefix: str = "out_charuco_plate"
