from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import math

import numpy as np

try:
    from PIL import Image, ImageDraw
except ModuleNotFoundError as exc:  # pragma: no cover - depends on local env
    Image = None
    ImageDraw = None
    _PIL_IMPORT_ERROR = exc
else:
    _PIL_IMPORT_ERROR = None

try:
    import trimesh
except ModuleNotFoundError as exc:  # pragma: no cover - depends on local env
    trimesh = None
    _TRIMESH_IMPORT_ERROR = exc
else:
    _TRIMESH_IMPORT_ERROR = None


DEFAULT_BODY_RGB = (242, 240, 235)
DEFAULT_ACCENT_RGB = (28, 30, 34)
DEFAULT_IMAGE_SIZE_PX = (1600, 1200)


@dataclass(frozen=True)
class PreviewMesh:
    mesh: trimesh.Trimesh
    fill_rgb: tuple[int, int, int]


def save_render_preview(
    meshes: tuple[PreviewMesh, ...] | list[PreviewMesh],
    path: str | Path,
    image_size_px: tuple[int, int] = DEFAULT_IMAGE_SIZE_PX,
) -> Path:
    _require_render_deps()

    preview_meshes = tuple(meshes)
    if not preview_meshes:
        raise ValueError("At least one preview mesh is required.")

    width_px, height_px = image_size_px
    if width_px <= 0 or height_px <= 0:
        raise ValueError("image_size_px values must be positive.")

    supersample = 2
    render_width_px = width_px * supersample
    render_height_px = height_px * supersample
    scene = _prepare_scene(preview_meshes)
    image = Image.new("RGB", (render_width_px, render_height_px), color=(248, 247, 243))
    draw = ImageDraw.Draw(image)

    light_dir = _normalize(np.array([0.45, -0.35, 0.82], dtype=float))
    margin_px = min(render_width_px, render_height_px) * 0.1
    scene_span_x = max(1e-6, scene["max_x"] - scene["min_x"])
    scene_span_y = max(1e-6, scene["max_y"] - scene["min_y"])
    scale = min(
        (render_width_px - 2.0 * margin_px) / scene_span_x,
        (render_height_px - 2.0 * margin_px) / scene_span_y,
    )
    center_x = (scene["min_x"] + scene["max_x"]) / 2.0
    center_y = (scene["min_y"] + scene["max_y"]) / 2.0

    triangles: list[tuple[float, list[tuple[int, int]], tuple[int, int, int]]] = []
    for vertices, faces, base_rgb in scene["meshes"]:
        for face in faces:
            tri = vertices[face]
            normal = np.cross(tri[1] - tri[0], tri[2] - tri[0])
            normal_len = np.linalg.norm(normal)
            if normal_len <= 1e-9:
                continue

            normal = normal / normal_len
            brightness = 0.3 + 0.7 * abs(float(np.dot(normal, light_dir)))
            color = _shade(base_rgb, brightness)
            polygon = [
                (
                    int(round((point[0] - center_x) * scale + render_width_px / 2.0)),
                    int(round(render_height_px / 2.0 - (point[1] - center_y) * scale)),
                )
                for point in tri
            ]
            depth = float(tri[:, 2].mean())
            triangles.append((depth, polygon, color))

    triangles.sort(key=lambda item: item[0])
    for _, polygon, color in triangles:
        draw.polygon(polygon, fill=color)

    image = image.resize((width_px, height_px), Image.Resampling.LANCZOS)
    output_path = Path(path)
    image.save(output_path)
    return output_path


def _prepare_scene(
    meshes: tuple[PreviewMesh, ...],
) -> dict[str, object]:
    all_vertices = [
        np.asarray(preview_mesh.mesh.vertices, dtype=float)
        for preview_mesh in meshes
        if len(preview_mesh.mesh.vertices) > 0
    ]
    if not all_vertices:
        raise ValueError("Preview meshes do not contain any vertices.")

    bounds_vertices = np.vstack(all_vertices)
    center = (bounds_vertices.min(axis=0) + bounds_vertices.max(axis=0)) / 2.0
    rotation = _camera_rotation_matrix()

    transformed_meshes: list[tuple[np.ndarray, np.ndarray, tuple[int, int, int]]] = []
    min_x = math.inf
    max_x = -math.inf
    min_y = math.inf
    max_y = -math.inf

    for preview_mesh in meshes:
        vertices = np.asarray(preview_mesh.mesh.vertices, dtype=float)
        faces = np.asarray(preview_mesh.mesh.faces, dtype=int)
        if len(vertices) == 0 or len(faces) == 0:
            continue

        rotated = (vertices - center) @ rotation.T
        min_x = min(min_x, float(rotated[:, 0].min()))
        max_x = max(max_x, float(rotated[:, 0].max()))
        min_y = min(min_y, float(rotated[:, 1].min()))
        max_y = max(max_y, float(rotated[:, 1].max()))
        transformed_meshes.append((rotated, faces, preview_mesh.fill_rgb))

    if not transformed_meshes:
        raise ValueError("Preview meshes do not contain any faces.")

    return {
        "meshes": transformed_meshes,
        "min_x": min_x,
        "max_x": max_x,
        "min_y": min_y,
        "max_y": max_y,
    }


def _camera_rotation_matrix() -> np.ndarray:
    yaw = math.radians(-38.0)
    pitch = math.radians(58.0)
    yaw_matrix = np.array(
        [
            [math.cos(yaw), -math.sin(yaw), 0.0],
            [math.sin(yaw), math.cos(yaw), 0.0],
            [0.0, 0.0, 1.0],
        ],
        dtype=float,
    )
    pitch_matrix = np.array(
        [
            [1.0, 0.0, 0.0],
            [0.0, math.cos(pitch), -math.sin(pitch)],
            [0.0, math.sin(pitch), math.cos(pitch)],
        ],
        dtype=float,
    )
    return pitch_matrix @ yaw_matrix


def _normalize(vector: np.ndarray) -> np.ndarray:
    vector_len = np.linalg.norm(vector)
    if vector_len <= 1e-9:
        raise ValueError("Cannot normalize a zero-length vector.")
    return vector / vector_len


def _shade(color: tuple[int, int, int], brightness: float) -> tuple[int, int, int]:
    return tuple(
        max(0, min(255, int(round(channel * brightness))))
        for channel in color
    )


def _require_render_deps() -> None:
    if trimesh is None:
        raise RuntimeError("trimesh is required to render preview images.") from _TRIMESH_IMPORT_ERROR
    if Image is None or ImageDraw is None:
        raise RuntimeError("Pillow is required to render preview images.") from _PIL_IMPORT_ERROR
