from __future__ import annotations

from dataclasses import dataclass

import numpy as np

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


def build_marker_black_rectangles(
    *,
    marker_id: int,
    marker_size_mm: float,
    aruco_marker_bits: int,
    aruco_border_bits: int,
    aruco_dict_name: str,
    aruco_image_size: int,
) -> tuple[Rectangle, ...]:
    _validate_marker_request(
        marker_size_mm=marker_size_mm,
        aruco_marker_bits=aruco_marker_bits,
        aruco_border_bits=aruco_border_bits,
        aruco_image_size=aruco_image_size,
    )

    marker_img = generate_aruco_image(
        aruco_dict_name=aruco_dict_name,
        marker_id=marker_id,
        aruco_image_size=aruco_image_size,
        aruco_border_bits=aruco_border_bits,
    )
    img_bin = _threshold_image(marker_img)

    cells_per_side = aruco_marker_bits + 2 * aruco_border_bits
    cell_size_mm = marker_size_mm / float(cells_per_side)
    rectangles: list[Rectangle] = []
    for marker_row in range(cells_per_side):
        for marker_col in range(cells_per_side):
            pixel = img_bin[
                int((marker_row + 0.5) * aruco_image_size / cells_per_side),
                int((marker_col + 0.5) * aruco_image_size / cells_per_side),
            ]
            if pixel != 0:
                continue
            rectangles.append(
                Rectangle(
                    x_mm=marker_col * cell_size_mm,
                    y_mm=(cells_per_side - 1 - marker_row) * cell_size_mm,
                    width_mm=cell_size_mm,
                    height_mm=cell_size_mm,
                )
            )

    if not rectangles:
        raise RuntimeError(f"No black geometry was generated for marker ID {marker_id}.")

    return tuple(rectangles)


def generate_aruco_image(
    *,
    aruco_dict_name: str,
    marker_id: int,
    aruco_image_size: int,
    aruco_border_bits: int,
) -> np.ndarray:
    _require_opencv()
    dictionary = _get_dictionary(aruco_dict_name)

    if hasattr(aruco, "generateImageMarker"):
        return aruco.generateImageMarker(
            dictionary,
            marker_id,
            aruco_image_size,
            borderBits=aruco_border_bits,
        )
    if hasattr(aruco, "drawMarker"):
        return aruco.drawMarker(
            dictionary,
            marker_id,
            aruco_image_size,
            borderBits=aruco_border_bits,
        )
    raise RuntimeError(
        "OpenCV ArUco API missing drawMarker/generateImageMarker. "
        "Install opencv-contrib-python."
    )


def _threshold_image(img: np.ndarray) -> np.ndarray:
    _require_opencv()
    _, img_bin = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)
    return img_bin


def _get_dictionary(aruco_dict_name: str):
    _require_opencv()
    try:
        dict_id = getattr(aruco, aruco_dict_name)
    except AttributeError as exc:
        raise ValueError(f"Unknown ArUco dictionary '{aruco_dict_name}'.") from exc
    return aruco.getPredefinedDictionary(dict_id)


def _require_opencv() -> None:
    if cv2 is None or aruco is None:
        raise RuntimeError(
            "opencv-contrib-python is required to generate ArUco markers."
        ) from _OPENCV_IMPORT_ERROR


def _validate_marker_request(
    *,
    marker_size_mm: float,
    aruco_marker_bits: int,
    aruco_border_bits: int,
    aruco_image_size: int,
) -> None:
    if marker_size_mm <= 0.0:
        raise ValueError("marker_size_mm must be positive.")
    if aruco_marker_bits <= 0:
        raise ValueError("aruco_marker_bits must be positive.")
    if aruco_border_bits < 0:
        raise ValueError("aruco_border_bits cannot be negative.")
    if aruco_image_size <= 0:
        raise ValueError("aruco_image_size must be positive.")
