from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import numpy as np


@dataclass(frozen=True)
class Association:
    rgb_timestamp: float
    rgb_path: str
    depth_timestamp: float
    depth_path: str


@dataclass(frozen=True)
class TimedPose:
    timestamp: float
    matrix: np.ndarray


def _iter_data_lines(path: str | Path) -> Iterable[list[str]]:
    with Path(path).open("r", encoding="utf-8") as handle:
        for raw in handle:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            yield line.split()


def load_timestamped_paths(path: str | Path) -> list[tuple[float, str]]:
    rows = []
    for fields in _iter_data_lines(path):
        if len(fields) >= 2:
            rows.append((float(fields[0]), fields[1]))
    return rows


def associate_timestamped_paths(first, second, max_difference: float = 0.02) -> list[Association]:
    candidates = []
    for i, (t1, _) in enumerate(first):
        for j, (t2, _) in enumerate(second):
            diff = abs(t1 - t2)
            if diff <= max_difference:
                candidates.append((diff, i, j))

    candidates.sort(key=lambda item: item[0])
    used_first, used_second = set(), set()
    matches = []
    for _, i, j in candidates:
        if i in used_first or j in used_second:
            continue
        used_first.add(i)
        used_second.add(j)
        t1, p1 = first[i]
        t2, p2 = second[j]
        matches.append(Association(t1, p1, t2, p2))

    matches.sort(key=lambda row: row.rgb_timestamp)
    return matches


def load_associations(path: str | Path) -> list[Association]:
    rows = []
    for fields in _iter_data_lines(path):
        if len(fields) >= 4:
            rows.append(Association(float(fields[0]), fields[1], float(fields[2]), fields[3]))
    return rows


def quaternion_xyzw_to_rotation(qx: float, qy: float, qz: float, qw: float) -> np.ndarray:
    q = np.array([qx, qy, qz, qw], dtype=np.float64)
    norm = np.linalg.norm(q)
    if norm == 0:
        raise ValueError("Quaternion has zero norm")
    q /= norm
    x, y, z, w = q
    return np.array(
        [
            [1 - 2 * (y*y + z*z), 2 * (x*y - z*w), 2 * (x*z + y*w)],
            [2 * (x*y + z*w), 1 - 2 * (x*x + z*z), 2 * (y*z - x*w)],
            [2 * (x*z - y*w), 2 * (y*z + x*w), 1 - 2 * (x*x + y*y)],
        ],
        dtype=np.float64,
    )


def pose_matrix_from_tum(fields: list[str]) -> np.ndarray:
    tx, ty, tz = map(float, fields[1:4])
    qx, qy, qz, qw = map(float, fields[4:8])
    transform = np.eye(4, dtype=np.float64)
    transform[:3, :3] = quaternion_xyzw_to_rotation(qx, qy, qz, qw)
    transform[:3, 3] = [tx, ty, tz]
    return transform


def load_tum_poses(path: str | Path) -> list[TimedPose]:
    poses = []
    for fields in _iter_data_lines(path):
        if len(fields) >= 8:
            poses.append(TimedPose(float(fields[0]), pose_matrix_from_tum(fields)))
    poses.sort(key=lambda p: p.timestamp)
    return poses


def nearest_pose(poses: list[TimedPose], timestamp: float, max_difference: float = 0.04) -> TimedPose | None:
    if not poses:
        return None
    times = np.fromiter((p.timestamp for p in poses), dtype=np.float64)
    index = int(np.searchsorted(times, timestamp))
    candidate_indices = []
    if index < len(poses):
        candidate_indices.append(index)
    if index > 0:
        candidate_indices.append(index - 1)
    best_index = min(candidate_indices, key=lambda i: abs(poses[i].timestamp - timestamp))
    best = poses[best_index]
    return best if abs(best.timestamp - timestamp) <= max_difference else None
