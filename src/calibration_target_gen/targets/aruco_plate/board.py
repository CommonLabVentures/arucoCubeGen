from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np

from .config import ArucoPlateConfig

try:
    import cv2
    from cv2 import aruco
except ModuleNotFoundError as exc:  # pragma: no cover - depends on local env
    cv2 = None
    aruco = None
    _OPENCV_IMPORT_ERROR = exc
else:
    _OPENCV_IMPORT_ERROR = None


@dataclass(frozen=True)
class Rectangle:
    x_mm: float
    y_mm: float
    width_mm: float
    height_mm: float


@dataclass(frozen=True)
class MarkerMetrics:
    marker_size_mm: float
    marker_origin_x_mm: float
    marker_origin_y_mm: float
    marker_margin_x_mm: float
    marker_margin_y_mm: float
    cell_size_mm: float
    cells_per_side: int
    marker_area_fraction: float


def build_marker_metrics(cfg: ArucoPlateConfig) -> MarkerMetrics:
    _validate_config(cfg)

    marker_size_mm = (
        float(cfg.marker_size_mm)
        if cfg.marker_size_mm is not None
        else min(float(cfg.plate_width_mm), float(cfg.plate_height_mm))
    )
    marker_margin_x_mm = (float(cfg.plate_width_mm) - marker_size_mm) / 2.0
    marker_margin_y_mm = (float(cfg.plate_height_mm) - marker_size_mm) / 2.0
    cells_per_side = cfg.aruco_marker_bits + 2 * cfg.aruco_border_bits
    cell_size_mm = marker_size_mm / float(cells_per_side)
    marker_area_fraction = (
        marker_size_mm * marker_size_mm / (float(cfg.plate_width_mm) * float(cfg.plate_height_mm))
    )

    return MarkerMetrics(
        marker_size_mm=marker_size_mm,
        marker_origin_x_mm=marker_margin_x_mm,
        marker_origin_y_mm=marker_margin_y_mm,
        marker_margin_x_mm=marker_margin_x_mm,
        marker_margin_y_mm=marker_margin_y_mm,
        cell_size_mm=cell_size_mm,
        cells_per_side=cells_per_side,
        marker_area_fraction=marker_area_fraction,
    )


def build_black_rectangles(cfg: ArucoPlateConfig) -> tuple[Rectangle, ...]:
    metrics = build_marker_metrics(cfg)
    marker_img = generate_aruco_image(cfg, cfg.marker_id)
    img_bin = _threshold_image(marker_img)

    rectangles: list[Rectangle] = []
    for marker_row in range(metrics.cells_per_side):
        for marker_col in range(metrics.cells_per_side):
            pixel = img_bin[
                int((marker_row + 0.5) * cfg.aruco_image_size / metrics.cells_per_side),
                int((marker_col + 0.5) * cfg.aruco_image_size / metrics.cells_per_side),
            ]
            if pixel != 0:
                continue
            rectangles.append(
                Rectangle(
                    x_mm=metrics.marker_origin_x_mm + marker_col * metrics.cell_size_mm,
                    y_mm=metrics.marker_origin_y_mm
                    + (metrics.cells_per_side - 1 - marker_row) * metrics.cell_size_mm,
                    width_mm=metrics.cell_size_mm,
                    height_mm=metrics.cell_size_mm,
                )
            )

    if not rectangles:
        raise RuntimeError(f"No black geometry was generated for marker ID {cfg.marker_id}.")

    return tuple(rectangles)


def render_preview_image(cfg: ArucoPlateConfig) -> np.ndarray:
    _validate_config(cfg)

    scale = int(cfg.preview_long_side_px) / max(float(cfg.plate_width_mm), float(cfg.plate_height_mm))
    image_width_px = max(1, int(round(float(cfg.plate_width_mm) * scale)))
    image_height_px = max(1, int(round(float(cfg.plate_height_mm) * scale)))
    image = np.full((image_height_px, image_width_px), 255, dtype=np.uint8)

    for rect in build_black_rectangles(cfg):
        x0 = max(0, min(image_width_px, int(round(rect.x_mm * scale))))
        x1 = max(0, min(image_width_px, int(round((rect.x_mm + rect.width_mm) * scale))))
        y0 = max(
            0,
            min(
                image_height_px,
                int(round((float(cfg.plate_height_mm) - rect.y_mm - rect.height_mm) * scale)),
            ),
        )
        y1 = max(
            0,
            min(image_height_px, int(round((float(cfg.plate_height_mm) - rect.y_mm) * scale))),
        )
        image[y0:y1, x0:x1] = 0

    return image


def save_preview_image(cfg: ArucoPlateConfig, path: Path) -> Path:
    _require_opencv()
    image = render_preview_image(cfg)
    if not cv2.imwrite(str(path), image):  # pragma: no cover - depends on local env
        raise RuntimeError(f"Failed to write preview image to {path}")
    return path


def generate_aruco_image(cfg: ArucoPlateConfig, marker_id: int) -> np.ndarray:
    _require_opencv()
    dictionary = _get_dictionary(cfg)

    if hasattr(aruco, "generateImageMarker"):
        return aruco.generateImageMarker(
            dictionary,
            marker_id,
            cfg.aruco_image_size,
            borderBits=cfg.aruco_border_bits,
        )
    if hasattr(aruco, "drawMarker"):
        return aruco.drawMarker(
            dictionary,
            marker_id,
            cfg.aruco_image_size,
            borderBits=cfg.aruco_border_bits,
        )
    raise RuntimeError(
        "OpenCV ArUco API missing drawMarker/generateImageMarker. "
        "Install opencv-contrib-python."
    )


def _threshold_image(img: np.ndarray) -> np.ndarray:
    _require_opencv()
    _, img_bin = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)
    return img_bin


def _get_dictionary(cfg: ArucoPlateConfig):
    _require_opencv()
    try:
        dict_id = getattr(aruco, cfg.aruco_dict_name)
    except AttributeError as exc:
        raise ValueError(f"Unknown ArUco dictionary '{cfg.aruco_dict_name}'.") from exc
    return aruco.getPredefinedDictionary(dict_id)


def _require_opencv() -> None:
    if cv2 is None or aruco is None:
        raise RuntimeError(
            "opencv-contrib-python is required to generate ArUco plate targets."
        ) from _OPENCV_IMPORT_ERROR


def _validate_config(cfg: ArucoPlateConfig) -> None:
    if cfg.plate_width_mm <= 0.0:
        raise ValueError("plate_width_mm must be positive.")
    if cfg.plate_height_mm <= 0.0:
        raise ValueError("plate_height_mm must be positive.")
    if cfg.plate_thickness_mm <= 0.0:
        raise ValueError("plate_thickness_mm must be positive.")
    if cfg.marker_size_mm is not None and cfg.marker_size_mm <= 0.0:
        raise ValueError("marker_size_mm must be positive when provided.")
    if cfg.marker_size_mm is not None and cfg.marker_size_mm > min(
        float(cfg.plate_width_mm), float(cfg.plate_height_mm)
    ):
        raise ValueError("marker_size_mm cannot exceed the smaller plate dimension.")
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
    if cfg.preview_long_side_px <= 0:
        raise ValueError("preview_long_side_px must be positive.")
