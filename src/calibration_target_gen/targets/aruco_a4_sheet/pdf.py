from __future__ import annotations

import math
from dataclasses import dataclass
from pathlib import Path

from .config import ArucoA4SheetConfig
from ...shared.aruco import build_marker_black_rectangles

_MM_TO_PT = 72.0 / 25.4


@dataclass(frozen=True)
class SheetLayout:
    page_width_mm: float
    page_height_mm: float
    marker_origin_x_mm: float
    marker_origin_y_mm: float
    marker_size_mm: float


def build_sheet_layout(cfg: ArucoA4SheetConfig) -> SheetLayout:
    _validate_config(cfg)

    return SheetLayout(
        page_width_mm=float(cfg.page_width_mm),
        page_height_mm=float(cfg.page_height_mm),
        marker_origin_x_mm=(float(cfg.page_width_mm) - float(cfg.marker_size_mm)) / 2.0,
        marker_origin_y_mm=(float(cfg.page_height_mm) - float(cfg.marker_size_mm)) / 2.0,
        marker_size_mm=float(cfg.marker_size_mm),
    )


def write_marker_sheet_pdf(cfg: ArucoA4SheetConfig, layout: SheetLayout, path: Path) -> Path:
    page_contents = [
        _build_page_content(cfg, layout, marker_id).encode("ascii")
        for marker_id in cfg.marker_ids
    ]
    pdf_bytes = _build_pdf_document(
        page_contents=page_contents,
        page_width_mm=layout.page_width_mm,
        page_height_mm=layout.page_height_mm,
    )
    path.write_bytes(pdf_bytes)
    return path


def _build_page_content(
    cfg: ArucoA4SheetConfig,
    layout: SheetLayout,
    marker_id: int,
) -> str:
    commands: list[str] = []
    commands.extend(_build_grid_commands(cfg, layout))
    commands.extend(_build_marker_commands(cfg, layout, marker_id))
    return "\n".join(commands) + "\n"


def _build_grid_commands(cfg: ArucoA4SheetConfig, layout: SheetLayout) -> list[str]:
    marker_x0 = layout.marker_origin_x_mm
    marker_x1 = layout.marker_origin_x_mm + layout.marker_size_mm
    marker_y0 = layout.marker_origin_y_mm
    marker_y1 = layout.marker_origin_y_mm + layout.marker_size_mm

    segments: list[tuple[float, float, float, float]] = []

    for x_mm in _grid_positions(
        origin_mm=layout.marker_origin_x_mm,
        step_mm=float(cfg.grid_spacing_mm),
        limit_mm=layout.page_width_mm,
    ):
        if marker_x0 <= x_mm <= marker_x1:
            segments.extend(
                (
                    (x_mm, 0.0, x_mm, marker_y0),
                    (x_mm, marker_y1, x_mm, layout.page_height_mm),
                )
            )
            continue
        segments.append((x_mm, 0.0, x_mm, layout.page_height_mm))

    for y_mm in _grid_positions(
        origin_mm=layout.marker_origin_y_mm,
        step_mm=float(cfg.grid_spacing_mm),
        limit_mm=layout.page_height_mm,
    ):
        if marker_y0 <= y_mm <= marker_y1:
            segments.extend(
                (
                    (0.0, y_mm, marker_x0, y_mm),
                    (marker_x1, y_mm, layout.page_width_mm, y_mm),
                )
            )
            continue
        segments.append((0.0, y_mm, layout.page_width_mm, y_mm))

    commands = [
        "q",
        f"{_format_number(float(cfg.grid_gray))} G",
        f"{_format_number(_mm_to_pt(float(cfg.grid_line_width_mm)))} w",
    ]
    for x0_mm, y0_mm, x1_mm, y1_mm in segments:
        if math.isclose(x0_mm, x1_mm) and math.isclose(y0_mm, y1_mm):
            continue
        commands.append(f"{_format_point(x0_mm, y0_mm)} m")
        commands.append(f"{_format_point(x1_mm, y1_mm)} l")
        commands.append("S")
    commands.append("Q")
    return commands


def _build_marker_commands(
    cfg: ArucoA4SheetConfig,
    layout: SheetLayout,
    marker_id: int,
) -> list[str]:
    rectangles = build_marker_black_rectangles(
        marker_id=marker_id,
        marker_size_mm=layout.marker_size_mm,
        aruco_marker_bits=cfg.aruco_marker_bits,
        aruco_border_bits=cfg.aruco_border_bits,
        aruco_dict_name=cfg.aruco_dict_name,
        aruco_image_size=cfg.aruco_image_size,
    )

    commands = ["q", "0 g"]
    for rect in rectangles:
        commands.append(
            "{} {} {} {} re f".format(
                _format_number(_mm_to_pt(layout.marker_origin_x_mm + rect.x_mm)),
                _format_number(_mm_to_pt(layout.marker_origin_y_mm + rect.y_mm)),
                _format_number(_mm_to_pt(rect.width_mm)),
                _format_number(_mm_to_pt(rect.height_mm)),
            )
        )
    commands.append("Q")
    return commands


def _build_pdf_document(
    *,
    page_contents: list[bytes],
    page_width_mm: float,
    page_height_mm: float,
) -> bytes:
    page_width_pt = _mm_to_pt(page_width_mm)
    page_height_pt = _mm_to_pt(page_height_mm)

    object_map: dict[int, bytes] = {
        1: b"<< /Type /Catalog /Pages 2 0 R >>",
    }

    next_object_id = 3
    page_ids: list[int] = []
    content_ids: list[int] = []
    for _ in page_contents:
        page_ids.append(next_object_id)
        content_ids.append(next_object_id + 1)
        next_object_id += 2

    kids = " ".join(f"{page_id} 0 R" for page_id in page_ids)
    object_map[2] = (
        f"<< /Type /Pages /Count {len(page_ids)} /Kids [ {kids} ] >>".encode("ascii")
    )

    for index, page_id in enumerate(page_ids):
        content_id = content_ids[index]
        object_map[page_id] = (
            "<< /Type /Page /Parent 2 0 R "
            f"/MediaBox [0 0 {_format_number(page_width_pt)} {_format_number(page_height_pt)}] "
            "/Resources << >> "
            f"/Contents {content_id} 0 R >>"
        ).encode("ascii")

        stream = page_contents[index]
        object_map[content_id] = (
            f"<< /Length {len(stream)} >>\n".encode("ascii")
            + b"stream\n"
            + stream
            + b"endstream"
        )

    info_object_id = next_object_id
    object_map[info_object_id] = (
        b"<< /Producer (arucoCubeGen) "
        b"/Creator (calibration_target_gen aruco_a4_sheet) "
        b"/Title (Printable A4 ArUco marker sheets) >>"
    )

    object_count = info_object_id
    document = bytearray(b"%PDF-1.4\n%\xe2\xe3\xcf\xd3\n")
    offsets = [0] * (object_count + 1)
    for object_id in range(1, object_count + 1):
        offsets[object_id] = len(document)
        document.extend(f"{object_id} 0 obj\n".encode("ascii"))
        document.extend(object_map[object_id])
        document.extend(b"\nendobj\n")

    xref_offset = len(document)
    document.extend(f"xref\n0 {object_count + 1}\n".encode("ascii"))
    document.extend(b"0000000000 65535 f \n")
    for object_id in range(1, object_count + 1):
        document.extend(f"{offsets[object_id]:010d} 00000 n \n".encode("ascii"))

    document.extend(
        (
            "trailer\n"
            f"<< /Size {object_count + 1} /Root 1 0 R /Info {info_object_id} 0 R >>\n"
            "startxref\n"
            f"{xref_offset}\n"
            "%%EOF\n"
        ).encode("ascii")
    )
    return bytes(document)


def _grid_positions(*, origin_mm: float, step_mm: float, limit_mm: float) -> tuple[float, ...]:
    start_index = math.ceil((0.0 - origin_mm) / step_mm)
    end_index = math.floor((limit_mm - origin_mm) / step_mm)
    return tuple(round(origin_mm + index * step_mm, 6) for index in range(start_index, end_index + 1))


def _mm_to_pt(value_mm: float) -> float:
    return value_mm * _MM_TO_PT


def _format_point(x_mm: float, y_mm: float) -> str:
    return f"{_format_number(_mm_to_pt(x_mm))} {_format_number(_mm_to_pt(y_mm))}"


def _format_number(value: float) -> str:
    return f"{value:.6f}".rstrip("0").rstrip(".")


def _validate_config(cfg: ArucoA4SheetConfig) -> None:
    if cfg.page_width_mm <= 0.0:
        raise ValueError("page_width_mm must be positive.")
    if cfg.page_height_mm <= 0.0:
        raise ValueError("page_height_mm must be positive.")
    if cfg.marker_size_mm <= 0.0:
        raise ValueError("marker_size_mm must be positive.")
    if cfg.marker_size_mm > min(float(cfg.page_width_mm), float(cfg.page_height_mm)):
        raise ValueError("marker_size_mm cannot exceed the smaller page dimension.")
    if not cfg.marker_ids:
        raise ValueError("marker_ids cannot be empty.")
    if any(marker_id < 0 for marker_id in cfg.marker_ids):
        raise ValueError("marker_ids must be non-negative.")
    if len(set(cfg.marker_ids)) != len(cfg.marker_ids):
        raise ValueError("marker_ids must be unique.")
    if cfg.aruco_marker_bits <= 0:
        raise ValueError("aruco_marker_bits must be positive.")
    if cfg.aruco_border_bits < 0:
        raise ValueError("aruco_border_bits cannot be negative.")
    if cfg.aruco_image_size <= 0:
        raise ValueError("aruco_image_size must be positive.")
    if cfg.grid_spacing_mm <= 0.0:
        raise ValueError("grid_spacing_mm must be positive.")
    if cfg.grid_line_width_mm <= 0.0:
        raise ValueError("grid_line_width_mm must be positive.")
    if not 0.0 <= cfg.grid_gray <= 1.0:
        raise ValueError("grid_gray must be in the range [0, 1].")
