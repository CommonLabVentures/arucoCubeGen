from __future__ import annotations

from .board import build_black_rectangles
from .config import CharucoPlateConfig

try:
    import trimesh
except ModuleNotFoundError as exc:  # pragma: no cover - depends on local env
    trimesh = None
    _TRIMESH_IMPORT_ERROR = exc
else:
    _TRIMESH_IMPORT_ERROR = None


def create_white_plate_mesh(cfg: CharucoPlateConfig) -> trimesh.Trimesh:
    _require_trimesh()
    plate = trimesh.creation.box(
        extents=(cfg.plate_size_mm, cfg.plate_size_mm, cfg.plate_thickness_mm)
    )
    plate.apply_translation(
        (
            cfg.plate_size_mm / 2.0,
            cfg.plate_size_mm / 2.0,
            cfg.plate_thickness_mm / 2.0,
        )
    )
    return plate


def create_black_inlay_mesh(cfg: CharucoPlateConfig) -> trimesh.Trimesh:
    _require_trimesh()
    meshes: list[trimesh.Trimesh] = []
    z_center_mm = cfg.plate_thickness_mm - cfg.black_inlay_depth_mm / 2.0

    for rect in build_black_rectangles(cfg):
        block = trimesh.creation.box(
            extents=(rect.width_mm, rect.height_mm, cfg.black_inlay_depth_mm)
        )
        block.apply_translation(
            (
                rect.x_mm + rect.width_mm / 2.0,
                rect.y_mm + rect.height_mm / 2.0,
                z_center_mm,
            )
        )
        meshes.append(block)

    if not meshes:
        raise RuntimeError("No black geometry was generated for the ChArUco plate.")

    return trimesh.util.concatenate(meshes)


def _require_trimesh() -> None:
    if trimesh is None:
        raise RuntimeError("trimesh is required to export ChArUco plate STL files.") from _TRIMESH_IMPORT_ERROR
