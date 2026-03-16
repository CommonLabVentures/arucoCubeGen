from __future__ import annotations

from datetime import datetime
from pathlib import Path

from .board import build_board_metrics, render_preview_image, required_marker_count, save_preview_image
from .config import CharucoPlateConfig
from .geometry import create_black_inlay_mesh, create_white_plate_mesh
from ...shared.render import (
    save_plate_render_preview,
)


def generate_all(cfg: CharucoPlateConfig) -> Path:
    output_dir = _make_output_dir(cfg.output_prefix)

    white_plate = create_white_plate_mesh(cfg)
    white_plate.export(output_dir / "charuco_plate_white.stl")

    black_inlay = create_black_inlay_mesh(cfg)
    black_inlay.export(output_dir / "charuco_plate_black.stl")

    preview_image = render_preview_image(cfg)
    save_preview_image(cfg, output_dir / "charuco_plate_preview.png")
    save_plate_render_preview(
        preview_image=preview_image,
        plate_width_mm=cfg.plate_size_mm,
        plate_height_mm=cfg.plate_size_mm,
        plate_thickness_mm=cfg.plate_thickness_mm,
        path=output_dir / "charuco_plate_render.png",
    )
    _write_run_info(output_dir, cfg)

    return output_dir.resolve()


def _make_output_dir(prefix: str) -> Path:
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_dir = Path(f"{prefix}_{timestamp}")
    output_dir.mkdir(parents=False, exist_ok=False)
    return output_dir


def _write_run_info(output_dir: Path, cfg: CharucoPlateConfig) -> Path:
    metrics = build_board_metrics(cfg)
    required_ids = required_marker_count(cfg)
    run_info_path = output_dir / "run_info.txt"

    lines = [
        "ChArUco Plate Generator - Run Info",
        "=" * 40,
        "",
        "Plate geometry:",
        f"  Plate size          : {cfg.plate_size_mm:.3f} mm x {cfg.plate_size_mm:.3f} mm",
        f"  Plate thickness     : {cfg.plate_thickness_mm:.3f} mm",
        f"  Black inlay depth   : {cfg.black_inlay_depth_mm:.3f} mm",
        "",
        "Board layout:",
        f"  Squares             : {cfg.board_squares_x} x {cfg.board_squares_y}",
        f"  Active board size   : {metrics.board_size_mm:.3f} mm",
        f"  Outer white margin  : {metrics.board_margin_mm:.3f} mm",
        f"  Square size         : {metrics.square_size_mm:.3f} mm",
        f"  Marker size         : {metrics.marker_size_mm:.3f} mm",
        f"  Marker quiet margin : {metrics.marker_margin_mm:.3f} mm",
        "",
        "ArUco settings:",
        f"  Dictionary          : {cfg.aruco_dict_name}",
        f"  Marker bits         : {cfg.aruco_marker_bits} x {cfg.aruco_marker_bits}",
        f"  Border bits         : {cfg.aruco_border_bits}",
        f"  Marker IDs needed   : {required_ids}",
        f"  Marker IDs used     : {', '.join(str(marker_id) for marker_id in cfg.marker_ids)}",
        "",
        "Artifacts:",
        "  charuco_plate_white.stl",
        "  charuco_plate_black.stl",
        "  charuco_plate_preview.png",
        "  charuco_plate_render.png",
        "  run_info.txt",
    ]

    run_info_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return run_info_path
