from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import math

import numpy as np

try:
    from PIL import Image, ImageDraw, ImageFilter
except ModuleNotFoundError as exc:  # pragma: no cover - depends on local env
    Image = None
    ImageDraw = None
    ImageFilter = None
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


def save_plate_render_preview(
    preview_image: np.ndarray,
    plate_width_mm: float,
    plate_height_mm: float,
    plate_thickness_mm: float,
    path: str | Path,
    image_size_px: tuple[int, int] = DEFAULT_IMAGE_SIZE_PX,
) -> Path:
    _require_pil()

    width_px, height_px = image_size_px
    if width_px <= 0 or height_px <= 0:
        raise ValueError("image_size_px values must be positive.")

    preview_rgba = Image.fromarray(preview_image).convert("RGBA")
    canvas = Image.new("RGBA", (width_px, height_px), color=(246, 245, 241, 255))
    top_quad, bottom_quad = _project_plate_quads(
        plate_width_mm=plate_width_mm,
        plate_height_mm=plate_height_mm,
        plate_thickness_mm=plate_thickness_mm,
        image_size_px=image_size_px,
    )

    shadow = Image.new("RGBA", (width_px, height_px), color=(0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_poly = [(x + width_px * 0.025, y + height_px * 0.03) for x, y in bottom_quad]
    shadow_draw.polygon(shadow_poly, fill=(0, 0, 0, 72))
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=max(8, int(min(width_px, height_px) * 0.018))))
    canvas.alpha_composite(shadow)

    front_edge_index = _select_edge(top_quad, mode="front")
    right_edge_index = _select_edge(top_quad, mode="right", exclude=front_edge_index)
    side_front = _side_quad(top_quad, bottom_quad, front_edge_index)
    side_right = _side_quad(top_quad, bottom_quad, right_edge_index)

    draw = ImageDraw.Draw(canvas)
    draw.polygon(side_front, fill=(226, 224, 220, 255))
    draw.polygon(side_right, fill=(214, 212, 208, 255))

    transform = preview_rgba.transform(
        (width_px, height_px),
        Image.Transform.AFFINE,
        _affine_coefficients(preview_rgba.size, top_quad),
        resample=Image.Resampling.BICUBIC,
        fillcolor=(0, 0, 0, 0),
    )
    canvas.alpha_composite(transform)

    draw = ImageDraw.Draw(canvas)
    draw.line([*top_quad, top_quad[0]], fill=(210, 208, 204, 255), width=max(1, width_px // 600))
    draw.line([*side_front, side_front[0]], fill=(190, 188, 184, 255), width=max(1, width_px // 800))
    draw.line([*side_right, side_right[0]], fill=(176, 174, 170, 255), width=max(1, width_px // 800))

    output_path = Path(path)
    canvas.convert("RGB").save(output_path)
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


def _project_plate_quads(
    plate_width_mm: float,
    plate_height_mm: float,
    plate_thickness_mm: float,
    image_size_px: tuple[int, int],
) -> tuple[list[tuple[float, float]], list[tuple[float, float]]]:
    width_px, height_px = image_size_px
    points_top = np.array(
        [
            [-plate_width_mm / 2.0, -plate_height_mm / 2.0, plate_thickness_mm],
            [plate_width_mm / 2.0, -plate_height_mm / 2.0, plate_thickness_mm],
            [plate_width_mm / 2.0, plate_height_mm / 2.0, plate_thickness_mm],
            [-plate_width_mm / 2.0, plate_height_mm / 2.0, plate_thickness_mm],
        ],
        dtype=float,
    )
    points_bottom = points_top.copy()
    points_bottom[:, 2] = 0.0

    rotation = _plate_rotation_matrix()
    top_projected = points_top @ rotation.T
    bottom_projected = points_bottom @ rotation.T

    all_points = np.vstack([top_projected[:, :2], bottom_projected[:, :2]])
    margin_px = min(width_px, height_px) * 0.08
    span_x = max(1e-6, float(all_points[:, 0].max() - all_points[:, 0].min()))
    span_y = max(1e-6, float(all_points[:, 1].max() - all_points[:, 1].min()))
    scale = min((width_px - 2.0 * margin_px) / span_x, (height_px - 2.0 * margin_px) / span_y)

    def to_screen(points: np.ndarray) -> list[tuple[float, float]]:
        centered = points[:, :2] - np.array(
            [
                (all_points[:, 0].min() + all_points[:, 0].max()) / 2.0,
                (all_points[:, 1].min() + all_points[:, 1].max()) / 2.0,
            ]
        )
        return [
            (
                float(width_px / 2.0 + point[0] * scale),
                float(height_px / 2.0 + point[1] * scale),
            )
            for point in centered
        ]

    return to_screen(top_projected), to_screen(bottom_projected)


def _plate_rotation_matrix() -> np.ndarray:
    yaw = math.radians(-36.0)
    pitch = math.radians(70.0)
    roll = math.radians(12.0)
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
    roll_matrix = np.array(
        [
            [math.cos(roll), 0.0, math.sin(roll)],
            [0.0, 1.0, 0.0],
            [-math.sin(roll), 0.0, math.cos(roll)],
        ],
        dtype=float,
    )
    return roll_matrix @ pitch_matrix @ yaw_matrix


def _select_edge(
    quad: list[tuple[float, float]],
    mode: str,
    exclude: int | None = None,
) -> int:
    edge_scores: list[tuple[float, int]] = []
    for index in range(len(quad)):
        if exclude is not None and index == exclude:
            continue
        x0, y0 = quad[index]
        x1, y1 = quad[(index + 1) % len(quad)]
        if mode == "front":
            score = (y0 + y1) / 2.0
        elif mode == "right":
            score = (x0 + x1) / 2.0
        else:
            raise ValueError(f"Unknown edge selection mode '{mode}'.")
        edge_scores.append((score, index))
    return max(edge_scores)[1]


def _side_quad(
    top_quad: list[tuple[float, float]],
    bottom_quad: list[tuple[float, float]],
    edge_index: int,
) -> list[tuple[float, float]]:
    next_index = (edge_index + 1) % len(top_quad)
    return [
        top_quad[edge_index],
        top_quad[next_index],
        bottom_quad[next_index],
        bottom_quad[edge_index],
    ]


def _affine_coefficients(
    source_size: tuple[int, int],
    destination_quad: list[tuple[float, float]],
) -> tuple[float, float, float, float, float, float]:
    src_width, src_height = source_size
    src_points = np.array(
        [
            [0.0, 0.0, 1.0],
            [float(src_width), 0.0, 1.0],
            [0.0, float(src_height), 1.0],
        ],
        dtype=float,
    )
    dst_points = np.array(
        [
            destination_quad[0],
            destination_quad[1],
            destination_quad[3],
        ],
        dtype=float,
    )
    x_params = np.linalg.solve(src_points, dst_points[:, 0])
    y_params = np.linalg.solve(src_points, dst_points[:, 1])
    forward = np.array(
        [
            [x_params[0], x_params[1], x_params[2]],
            [y_params[0], y_params[1], y_params[2]],
            [0.0, 0.0, 1.0],
        ],
        dtype=float,
    )
    inverse = np.linalg.inv(forward)
    return (
        float(inverse[0, 0]),
        float(inverse[0, 1]),
        float(inverse[0, 2]),
        float(inverse[1, 0]),
        float(inverse[1, 1]),
        float(inverse[1, 2]),
    )


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


def _require_pil() -> None:
    if Image is None or ImageDraw is None or ImageFilter is None:
        raise RuntimeError("Pillow is required to render plate preview images.") from _PIL_IMPORT_ERROR
