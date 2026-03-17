from __future__ import annotations

from datetime import datetime
from pathlib import Path

from .config import ArucoA4SheetConfig
from .pdf import SheetLayout, build_sheet_layout, write_marker_sheet_pdf


def generate_all(cfg: ArucoA4SheetConfig) -> Path:
    layout = build_sheet_layout(cfg)
    output_dir = _make_output_dir(cfg.output_prefix)

    pdf_path = output_dir / _build_pdf_filename(cfg)
    write_marker_sheet_pdf(cfg, layout, pdf_path)
    _write_run_info(output_dir, cfg, layout, pdf_path.name)

    return output_dir.resolve()


def _make_output_dir(prefix: str) -> Path:
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_dir = Path(f"{prefix}_{timestamp}")
    output_dir.mkdir(parents=False, exist_ok=False)
    return output_dir


def _build_pdf_filename(cfg: ArucoA4SheetConfig) -> str:
    if len(cfg.marker_ids) == 1:
        return f"aruco_a4_sheet_id_{cfg.marker_ids[0]}.pdf"

    expected_ids = tuple(range(cfg.marker_ids[0], cfg.marker_ids[-1] + 1))
    if cfg.marker_ids == expected_ids:
        return f"aruco_a4_sheets_id_{cfg.marker_ids[0]}_to_{cfg.marker_ids[-1]}.pdf"

    return "aruco_a4_sheets.pdf"


def _write_run_info(
    output_dir: Path,
    cfg: ArucoA4SheetConfig,
    layout: SheetLayout,
    pdf_name: str,
) -> Path:
    run_info_path = output_dir / "run_info.txt"

    lines = [
        "Printable A4 ArUco Sheet Generator - Run Info",
        "=" * 48,
        "",
        "Paper / PDF:",
        f"  Page size           : {cfg.page_width_mm:.3f} mm x {cfg.page_height_mm:.3f} mm",
        f"  Marker size         : {cfg.marker_size_mm:.3f} mm x {cfg.marker_size_mm:.3f} mm",
        f"  Marker origin       : x={layout.marker_origin_x_mm:.3f} mm, y={layout.marker_origin_y_mm:.3f} mm",
        f"  Grid spacing        : {cfg.grid_spacing_mm:.3f} mm",
        f"  Grid line width     : {cfg.grid_line_width_mm:.3f} mm",
        "",
        "ArUco settings:",
        f"  Dictionary          : {cfg.aruco_dict_name}",
        f"  Marker bits         : {cfg.aruco_marker_bits} x {cfg.aruco_marker_bits}",
        f"  Border bits         : {cfg.aruco_border_bits}",
        f"  Marker IDs          : {', '.join(str(marker_id) for marker_id in cfg.marker_ids)}",
        "",
        "Print notes:",
        "  Print at 100% / Actual size.",
        "  Disable fit-to-page, shrinking, and paper scaling.",
        "",
        "Artifacts:",
        f"  {pdf_name}",
        "  run_info.txt",
    ]

    run_info_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return run_info_path
