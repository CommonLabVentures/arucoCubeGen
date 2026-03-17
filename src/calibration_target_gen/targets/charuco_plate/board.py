from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np

from .config import CharucoPlateConfig
from ...shared.aruco import Rectangle, build_marker_black_rectangles

try:
    import cv2
except ModuleNotFoundError as exc:  # pragma: no cover - depends on local env
    cv2 = None
    _OPENCV_IMPORT_ERROR = exc
else:
    _OPENCV_IMPORT_ERROR = None


@dataclass(frozen=True)
class BoardMetrics:
    board_size_mm: float
    board_margin_mm: float
    square_size_mm: float
    marker_size_mm: float
    marker_margin_mm: float


def build_board_metrics(cfg: CharucoPlateConfig) -> BoardMetrics:
    _validate_config(cfg)

    board_size_mm = float(cfg.plate_size_mm) * float(cfg.board_margin_fraction)
    board_margin_mm = (float(cfg.plate_size_mm) - board_size_mm) / 2.0
    square_size_mm = board_size_mm / float(cfg.board_squares_x)
    marker_size_mm = square_size_mm * float(cfg.marker_length_fraction)
    marker_margin_mm = (square_size_mm - marker_size_mm) / 2.0

    return BoardMetrics(
        board_size_mm=board_size_mm,
        board_margin_mm=board_margin_mm,
        square_size_mm=square_size_mm,
        marker_size_mm=marker_size_mm,
        marker_margin_mm=marker_margin_mm,
    )


def required_marker_count(cfg: CharucoPlateConfig) -> int:
    _validate_config(cfg)
    return sum(
        1
        for row in range(cfg.board_squares_y)
        for col in range(cfg.board_squares_x)
        if _square_has_marker(row, col, cfg)
    )


def build_black_rectangles(cfg: CharucoPlateConfig) -> tuple[Rectangle, ...]:
    _validate_config(cfg)
    metrics = build_board_metrics(cfg)
    marker_count = required_marker_count(cfg)
    if len(cfg.marker_ids) != marker_count:
        raise ValueError(
            f"Expected {marker_count} marker IDs for a "
            f"{cfg.board_squares_x}x{cfg.board_squares_y} ChArUco board, "
            f"got {len(cfg.marker_ids)}."
        )

    rectangles: list[Rectangle] = []
    marker_ids = iter(cfg.marker_ids)
    marker_cache: dict[int, tuple[Rectangle, ...]] = {}

    for board_row in range(cfg.board_squares_y):
        for board_col in range(cfg.board_squares_x):
            square_x_mm, square_y_mm = _square_origin_mm(board_row, board_col, metrics, cfg)
            if _square_is_black(board_row, board_col, cfg):
                rectangles.append(
                    Rectangle(
                        x_mm=square_x_mm,
                        y_mm=square_y_mm,
                        width_mm=metrics.square_size_mm,
                        height_mm=metrics.square_size_mm,
                    )
                )
                continue

            marker_id = next(marker_ids)
            marker_rectangles = marker_cache.get(marker_id)
            if marker_rectangles is None:
                marker_rectangles = build_marker_black_rectangles(
                    marker_id=marker_id,
                    marker_size_mm=metrics.marker_size_mm,
                    aruco_marker_bits=cfg.aruco_marker_bits,
                    aruco_border_bits=cfg.aruco_border_bits,
                    aruco_dict_name=cfg.aruco_dict_name,
                    aruco_image_size=cfg.aruco_image_size,
                )
                marker_cache[marker_id] = marker_rectangles

            marker_x_mm = square_x_mm + metrics.marker_margin_mm
            marker_y_mm = square_y_mm + metrics.marker_margin_mm
            for rect in marker_rectangles:
                rectangles.append(
                    Rectangle(
                        x_mm=marker_x_mm + rect.x_mm,
                        y_mm=marker_y_mm + rect.y_mm,
                        width_mm=rect.width_mm,
                        height_mm=rect.height_mm,
                    )
                )

    return tuple(rectangles)


def render_preview_image(cfg: CharucoPlateConfig) -> np.ndarray:
    _validate_config(cfg)

    image_size_px = int(cfg.preview_image_size_px)
    image = np.full((image_size_px, image_size_px), 255, dtype=np.uint8)
    scale = image_size_px / float(cfg.plate_size_mm)

    for rect in build_black_rectangles(cfg):
        x0 = max(0, min(image_size_px, int(round(rect.x_mm * scale))))
        x1 = max(0, min(image_size_px, int(round((rect.x_mm + rect.width_mm) * scale))))
        y0 = max(
            0,
            min(
                image_size_px,
                int(round((float(cfg.plate_size_mm) - rect.y_mm - rect.height_mm) * scale)),
            ),
        )
        y1 = max(
            0,
            min(image_size_px, int(round((float(cfg.plate_size_mm) - rect.y_mm) * scale))),
        )
        image[y0:y1, x0:x1] = 0

    return image


def save_preview_image(cfg: CharucoPlateConfig, path: Path) -> Path:
    _require_opencv()
    image = render_preview_image(cfg)
    if not cv2.imwrite(str(path), image):  # pragma: no cover - depends on local env
        raise RuntimeError(f"Failed to write preview image to {path}")
    return path


def _require_opencv() -> None:
    if cv2 is None:
        raise RuntimeError(
            "opencv-contrib-python is required to generate ChArUco targets."
        ) from _OPENCV_IMPORT_ERROR


def _square_origin_mm(
    board_row: int,
    board_col: int,
    metrics: BoardMetrics,
    cfg: CharucoPlateConfig,
) -> tuple[float, float]:
    x_mm = metrics.board_margin_mm + board_col * metrics.square_size_mm
    y_mm = metrics.board_margin_mm + (cfg.board_squares_y - 1 - board_row) * metrics.square_size_mm
    return x_mm, y_mm


def _square_has_marker(board_row: int, board_col: int, cfg: CharucoPlateConfig) -> bool:
    return not _square_is_black(board_row, board_col, cfg)


def _square_is_black(board_row: int, board_col: int, cfg: CharucoPlateConfig) -> bool:
    starts_black = bool(cfg.top_left_square_black)
    even_parity = (board_row + board_col) % 2 == 0
    return even_parity if starts_black else not even_parity


def _validate_config(cfg: CharucoPlateConfig) -> None:
    if cfg.plate_size_mm <= 0.0:
        raise ValueError("plate_size_mm must be positive.")
    if cfg.plate_thickness_mm <= 0.0:
        raise ValueError("plate_thickness_mm must be positive.")
    if cfg.board_squares_x != cfg.board_squares_y:
        raise ValueError("This target expects a square ChArUco matrix, so board_squares_x must equal board_squares_y.")
    if cfg.board_squares_x < 2 or cfg.board_squares_y < 2:
        raise ValueError("board_squares_x and board_squares_y must be at least 2.")
    if not 0.0 < cfg.board_margin_fraction <= 1.0:
        raise ValueError("board_margin_fraction must be in the range (0, 1].")
    if not 0.0 < cfg.marker_length_fraction < 1.0:
        raise ValueError("marker_length_fraction must be in the range (0, 1).")
    if cfg.aruco_marker_bits <= 0:
        raise ValueError("aruco_marker_bits must be positive.")
    if cfg.aruco_border_bits < 0:
        raise ValueError("aruco_border_bits cannot be negative.")
    if cfg.aruco_image_size <= 0:
        raise ValueError("aruco_image_size must be positive.")
    if cfg.black_inlay_depth_mm <= 0.0:
        raise ValueError("black_inlay_depth_mm must be positive.")
    if cfg.black_inlay_depth_mm > cfg.plate_thickness_mm:
        raise ValueError("black_inlay_depth_mm cannot exceed plate_thickness_mm.")
    if cfg.preview_image_size_px <= 0:
        raise ValueError("preview_image_size_px must be positive.")
