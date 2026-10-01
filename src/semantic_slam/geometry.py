from __future__ import annotations

import numpy as np


def depth_pixels_to_camera_points(
    u: np.ndarray,
    v: np.ndarray,
    depth_m: np.ndarray,
    fx: float,
    fy: float,
    cx: float,
    cy: float,
) -> np.ndarray:
    x = (u.astype(np.float64) - cx) * depth_m / fx
    y = (v.astype(np.float64) - cy) * depth_m / fy
    z = depth_m.astype(np.float64)
    return np.column_stack((x, y, z))


def transform_points(points: np.ndarray, transform: np.ndarray) -> np.ndarray:
    if points.size == 0:
        return np.empty((0, 3), dtype=np.float64)
    homogeneous = np.column_stack((points, np.ones(len(points), dtype=np.float64)))
    transformed = (transform @ homogeneous.T).T
    return transformed[:, :3]


def sampled_depth_points(
    depth_raw: np.ndarray,
    fx: float,
    fy: float,
    cx: float,
    cy: float,
    depth_scale: float,
    stride: int,
    min_depth_m: float,
    max_depth_m: float,
    excluded_mask: np.ndarray | None = None,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    height, width = depth_raw.shape[:2]
    vv, uu = np.mgrid[0:height:stride, 0:width:stride]
    sampled_depth = depth_raw[vv, uu].astype(np.float64) / depth_scale
    valid = (sampled_depth >= min_depth_m) & (sampled_depth <= max_depth_m)
    if excluded_mask is not None:
        valid &= ~excluded_mask[vv, uu]

    u = uu[valid]
    v = vv[valid]
    z = sampled_depth[valid]
    points = depth_pixels_to_camera_points(u, v, z, fx, fy, cx, cy)
    return points, v, u


def masked_3d_centroid(
    mask: np.ndarray,
    depth_raw: np.ndarray,
    fx: float,
    fy: float,
    cx: float,
    cy: float,
    depth_scale: float,
    min_depth_m: float,
    max_depth_m: float,
    max_samples: int = 4000,
) -> np.ndarray | None:
    v, u = np.nonzero(mask)
    if len(u) == 0:
        return None

    depths = depth_raw[v, u].astype(np.float64) / depth_scale
    valid = (depths >= min_depth_m) & (depths <= max_depth_m)
    u = u[valid]
    v = v[valid]
    depths = depths[valid]
    if len(depths) < 10:
        return None

    if len(depths) > max_samples:
        step = max(1, len(depths) // max_samples)
        u = u[::step]
        v = v[::step]
        depths = depths[::step]

    points = depth_pixels_to_camera_points(u, v, depths, fx, fy, cx, cy)
    return np.median(points, axis=0)


def umeyama_rigid_alignment(source: np.ndarray, target: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    if source.shape != target.shape or source.ndim != 2 or source.shape[1] != 3:
        raise ValueError("source and target must have shape (N, 3)")
    if len(source) < 3:
        raise ValueError("At least 3 points are required for rigid alignment")

    src_mean = source.mean(axis=0)
    tgt_mean = target.mean(axis=0)
    src_centered = source - src_mean
    tgt_centered = target - tgt_mean
    covariance = (tgt_centered.T @ src_centered) / len(source)
    u, _, vt = np.linalg.svd(covariance)
    correction = np.eye(3)
    if np.linalg.det(u @ vt) < 0:
        correction[-1, -1] = -1
    rotation = u @ correction @ vt
    translation = tgt_mean - rotation @ src_mean
    return rotation, translation
