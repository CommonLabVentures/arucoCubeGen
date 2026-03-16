import os
import trimesh

from src.calibration_target_gen.shared.render import (
    DEFAULT_ACCENT_RGB,
    DEFAULT_BODY_RGB,
    PreviewMesh,
    save_render_preview,
)

from .config import Config
from .geometry import create_cube_with_slots, create_plate_base
from .aruco_marker import create_marker_mesh_for_plate
from .io_utils import make_output_dir, write_run_info

def generate_all(cfg: Config) -> str:
    out_dir = make_output_dir("out_stls")
    print(f"Saving STL outputs to: {out_dir}")

    # Cube
    cube = create_cube_with_slots(cfg)
    cube.export(os.path.join(out_dir, "cube_with_slots.stl"))
    save_render_preview(
        [PreviewMesh(mesh=cube, fill_rgb=DEFAULT_BODY_RGB)],
        os.path.join(out_dir, "cube_render.png"),
    )

    # Plate template (also gives us plate_size)
    plate_template, plate_size, plate_thickness = create_plate_base(cfg, text=None)
    plate_template.export(os.path.join(out_dir, "plate_base.stl"))

    preview_plate_id = cfg.plate_ids[0] if cfg.plate_ids else None
    if preview_plate_id is not None:
        preview_label = f"{cfg.bezel_text_prefix}{preview_plate_id}" if cfg.bezel_text_enabled else None
        preview_base, _, _ = create_plate_base(cfg, text=preview_label)
        preview_marker = create_marker_mesh_for_plate(cfg, preview_plate_id, plate_size, plate_thickness)
        save_render_preview(
            [
                PreviewMesh(mesh=preview_base, fill_rgb=DEFAULT_BODY_RGB),
                PreviewMesh(mesh=preview_marker, fill_rgb=DEFAULT_ACCENT_RGB),
            ],
            os.path.join(out_dir, "plate_render.png"),
        )

    # Run metadata
    write_run_info(out_dir, cfg, plate_size, plate_thickness, preview_plate_id=preview_plate_id)

    # Per-ID exports
    for mid in cfg.plate_ids:
        label = f"{cfg.bezel_text_prefix}{mid}" if cfg.bezel_text_enabled else None

        base, _, _ = create_plate_base(cfg, text=label)
        base.export(os.path.join(out_dir, f"plate_base_id{mid}.stl"))

        marker = create_marker_mesh_for_plate(cfg, mid, plate_size, plate_thickness)
        marker.export(os.path.join(out_dir, f"plate_marker_id{mid}.stl"))

        combined = trimesh.util.concatenate([base, marker])
        combined.export(os.path.join(out_dir, f"plate_combined_id{mid}.stl"))

    return out_dir
