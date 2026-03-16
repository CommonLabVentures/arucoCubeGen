from __future__ import annotations

from datetime import datetime
from pathlib import Path

from .board import build_marker_metrics, save_preview_image
from .config import ArucoPlateConfig
from .geometry import create_black_inlay_mesh, create_white_plate_mesh
from ...shared.render import (
    DEFAULT_ACCENT_RGB,
    DEFAULT_BODY_RGB,
    PreviewMesh,
    save_render_preview,
)


def generate_all(cfg: ArucoPlateConfig) -> Path:
    output_dir = _make_output_dir(cfg.output_prefix)

    white_plate = create_white_plate_mesh(cfg)
    white_plate.export(output_dir / "aruco_plate_white.stl")

    black_inlay = create_black_inlay_mesh(cfg)
    black_inlay.export(output_dir / "aruco_plate_black.stl")

    save_preview_image(cfg, output_dir / "aruco_plate_preview.png")
    save_render_preview(
        [
            PreviewMesh(mesh=white_plate, fill_rgb=DEFAULT_BODY_RGB),
            PreviewMesh(mesh=black_inlay, fill_rgb=DEFAULT_ACCENT_RGB),
        ],
        output_dir / "aruco_plate_render.png",
    )
    _write_run_info(output_dir, cfg)

    return output_dir.resolve()


def _make_output_dir(prefix: str) -> Path:
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_dir = Path(f"{prefix}_{timestamp}")
    output_dir.mkdir(parents=False, exist_ok=False)
    return output_dir


def _write_run_info(output_dir: Path, cfg: ArucoPlateConfig) -> Path:
    metrics = build_marker_metrics(cfg)
    run_info_path = output_dir / "run_info.txt"

    lines = [
        "ArUco Plate Generator - Run Info",
        "=" * 38,
        "",
        "Plate geometry:",
        f"  Plate size          : {cfg.plate_width_mm:.3f} mm x {cfg.plate_height_mm:.3f} mm",
        f"  Plate thickness     : {cfg.plate_thickness_mm:.3f} mm",
        f"  Black inlay depth   : {cfg.black_inlay_depth_mm:.3f} mm",
        "",
        "Marker layout:",
        f"  Marker ID           : {cfg.marker_id}",
        f"  Marker size         : {metrics.marker_size_mm:.3f} mm",
        f"  Left/right margin   : {metrics.marker_margin_x_mm:.3f} mm",
        f"  Top/bottom margin   : {metrics.marker_margin_y_mm:.3f} mm",
        f"  Cell size           : {metrics.cell_size_mm:.3f} mm",
        f"  Plate area usage    : {metrics.marker_area_fraction * 100.0:.2f}%",
        "",
        "ArUco settings:",
        f"  Dictionary          : {cfg.aruco_dict_name}",
        f"  Marker bits         : {cfg.aruco_marker_bits} x {cfg.aruco_marker_bits}",
        f"  Border bits         : {cfg.aruco_border_bits}",
        "",
        "Artifacts:",
        "  aruco_plate_white.stl",
        "  aruco_plate_black.stl",
        "  aruco_plate_preview.png",
        "  aruco_plate_render.png",
        "  run_info.txt",
    ]

    run_info_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return run_info_path
