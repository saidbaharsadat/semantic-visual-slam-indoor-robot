from __future__ import annotations

from pathlib import Path

import numpy as np


def voxel_downsample(
    points: np.ndarray,
    colors: np.ndarray,
    voxel_size: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Average XYZ and RGB values inside a regular voxel grid."""
    points = np.asarray(points, dtype=np.float64)
    colors = np.asarray(colors, dtype=np.float64)

    if points.ndim != 2 or points.shape[1] != 3:
        raise ValueError("points must have shape (N, 3)")
    if colors.shape != points.shape:
        raise ValueError("colors must have the same shape as points")
    if len(points) == 0 or voxel_size <= 0:
        return points.copy(), colors.copy()

    voxel_index = np.floor(points / float(voxel_size)).astype(np.int64)
    _, inverse = np.unique(voxel_index, axis=0, return_inverse=True)
    count = np.bincount(inverse).astype(np.float64)

    point_sum = np.zeros((len(count), 3), dtype=np.float64)
    color_sum = np.zeros((len(count), 3), dtype=np.float64)
    np.add.at(point_sum, inverse, points)
    np.add.at(color_sum, inverse, colors)

    return point_sum / count[:, None], color_sum / count[:, None]


def write_ply(path: str | Path, points: np.ndarray, colors: np.ndarray) -> None:
    """Write an RGB point cloud as binary little-endian PLY without GUI dependencies."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    points = np.asarray(points, dtype=np.float32)
    colors = np.asarray(colors, dtype=np.float64)
    if points.ndim != 2 or points.shape[1] != 3:
        raise ValueError("points must have shape (N, 3)")
    if colors.shape != points.shape:
        raise ValueError("colors must have the same shape as points")

    rgb = np.clip(np.rint(colors * 255.0), 0, 255).astype(np.uint8)
    vertices = np.empty(
        len(points),
        dtype=[
            ("x", "<f4"),
            ("y", "<f4"),
            ("z", "<f4"),
            ("red", "u1"),
            ("green", "u1"),
            ("blue", "u1"),
        ],
    )
    vertices["x"] = points[:, 0]
    vertices["y"] = points[:, 1]
    vertices["z"] = points[:, 2]
    vertices["red"] = rgb[:, 0]
    vertices["green"] = rgb[:, 1]
    vertices["blue"] = rgb[:, 2]

    header = (
        "ply\n"
        "format binary_little_endian 1.0\n"
        f"element vertex {len(vertices)}\n"
        "property float x\n"
        "property float y\n"
        "property float z\n"
        "property uchar red\n"
        "property uchar green\n"
        "property uchar blue\n"
        "end_header\n"
    ).encode("ascii")

    with path.open("wb") as handle:
        handle.write(header)
        vertices.tofile(handle)
