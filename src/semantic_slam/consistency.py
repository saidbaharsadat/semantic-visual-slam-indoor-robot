from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class SpatialCluster:
    class_name: str
    points: list[np.ndarray]
    timestamps: list[float]

    @property
    def centroid(self) -> np.ndarray:
        return np.mean(np.asarray(self.points, dtype=np.float64), axis=0)


def cluster_observations(
    observations: list[tuple[float, str, np.ndarray]],
    radius_m: float = 0.6,
) -> list[SpatialCluster]:
    """Group same-class 3D observations into simple spatial clusters."""
    clusters: list[SpatialCluster] = []

    for timestamp, class_name, point in sorted(observations, key=lambda item: item[0]):
        point = np.asarray(point, dtype=np.float64)
        candidates = [cluster for cluster in clusters if cluster.class_name == class_name]

        if candidates:
            distances = [np.linalg.norm(point - cluster.centroid) for cluster in candidates]
            best_index = int(np.argmin(distances))
            if distances[best_index] <= radius_m:
                candidates[best_index].points.append(point)
                candidates[best_index].timestamps.append(float(timestamp))
                continue

        clusters.append(
            SpatialCluster(
                class_name=class_name,
                points=[point],
                timestamps=[float(timestamp)],
            )
        )

    return clusters


def summarize_cluster(cluster: SpatialCluster) -> dict:
    points = np.asarray(cluster.points, dtype=np.float64)
    centroid = np.mean(points, axis=0)
    distances = np.linalg.norm(points - centroid, axis=1)

    return {
        "class_name": cluster.class_name,
        "observations": int(len(points)),
        "centroid_m": [float(value) for value in centroid],
        "mean_position_deviation_m": float(np.mean(distances)),
        "rms_position_deviation_m": float(np.sqrt(np.mean(distances ** 2))),
        "max_position_deviation_m": float(np.max(distances)),
        "time_span_s": float(max(cluster.timestamps) - min(cluster.timestamps)),
    }
