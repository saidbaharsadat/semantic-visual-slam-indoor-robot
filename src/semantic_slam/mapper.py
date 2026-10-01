from __future__ import annotations

import csv
import json
from collections import Counter
from dataclasses import asdict, dataclass
from pathlib import Path

import cv2
import numpy as np

from .detector import Detection
from .geometry import masked_3d_centroid, sampled_depth_points, transform_points
from .pointcloud import voxel_downsample, write_ply


@dataclass
class ObjectObservation:
    timestamp: float
    class_name: str
    confidence: float
    x: float
    y: float
    z: float
    is_dynamic: bool


@dataclass
class FrameSummary:
    timestamp: float
    points_added: int
    detections: int
    dynamic_detections: int


class SemanticMapper:
    def __init__(self, config: dict) -> None:
        self.camera = config["camera"]
        self.mapping = config["mapping"]
        self.dynamic_classes = set(config["detector"].get("dynamic_classes", ["person"]))
        self._points = []
        self._colors = []
        self.object_observations = []
        self.frame_summaries = []

    def process_frame(self, timestamp, image_bgr, depth_raw, twc, detections, filter_dynamic):
        dynamic_mask = np.zeros(depth_raw.shape[:2], dtype=bool)
        dynamic_count = 0

        for detection in detections:
            is_dynamic = detection.class_name in self.dynamic_classes
            if is_dynamic:
                dynamic_count += 1
                dynamic_mask |= detection.mask

            centroid_camera = masked_3d_centroid(
                detection.mask, depth_raw,
                fx=float(self.camera["fx"]), fy=float(self.camera["fy"]),
                cx=float(self.camera["cx"]), cy=float(self.camera["cy"]),
                depth_scale=float(self.camera["depth_scale"]),
                min_depth_m=float(self.mapping["min_depth_m"]),
                max_depth_m=float(self.mapping["max_depth_m"]),
            )
            if centroid_camera is not None:
                centroid_world = transform_points(centroid_camera.reshape(1, 3), twc)[0]
                self.object_observations.append(ObjectObservation(
                    timestamp, detection.class_name, detection.confidence,
                    float(centroid_world[0]), float(centroid_world[1]), float(centroid_world[2]),
                    is_dynamic,
                ))

        points_camera, v, u = sampled_depth_points(
            depth_raw,
            fx=float(self.camera["fx"]), fy=float(self.camera["fy"]),
            cx=float(self.camera["cx"]), cy=float(self.camera["cy"]),
            depth_scale=float(self.camera["depth_scale"]),
            stride=int(self.mapping["pixel_stride"]),
            min_depth_m=float(self.mapping["min_depth_m"]),
            max_depth_m=float(self.mapping["max_depth_m"]),
            excluded_mask=dynamic_mask if filter_dynamic else None,
        )
        points_world = transform_points(points_camera, twc)
        colors_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)[v, u].astype(np.float64) / 255.0

        if len(points_world):
            self._points.append(points_world)
            self._colors.append(colors_rgb)

        self.frame_summaries.append(FrameSummary(timestamp, int(len(points_world)), len(detections), dynamic_count))

    def save(self, output_dir: str | Path, metadata: dict | None = None) -> dict:
        output = Path(output_dir)
        output.mkdir(parents=True, exist_ok=True)
        if not self._points:
            raise RuntimeError("No 3D points were accumulated. Check poses, depth, and configuration.")

        points = np.concatenate(self._points, axis=0)
        colors = np.concatenate(self._colors, axis=0)
        before = len(points)

        voxel_size = float(self.mapping["voxel_size_m"])
        points_out, colors_out = voxel_downsample(points, colors, voxel_size)
        write_ply(output / "semantic_map.ply", points_out, colors_out)

        with (output / "object_observations.csv").open("w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(["timestamp", "class", "confidence", "x", "y", "z", "is_dynamic"])
            for item in self.object_observations:
                writer.writerow([item.timestamp, item.class_name, item.confidence, item.x, item.y, item.z, int(item.is_dynamic)])

        with (output / "frame_summary.csv").open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(asdict(self.frame_summaries[0]).keys()))
            writer.writeheader()
            for item in self.frame_summaries:
                writer.writerow(asdict(item))

        class_counts = Counter(item.class_name for item in self.object_observations)
        confidences = [item.confidence for item in self.object_observations]
        object_summary = {
            "total_observations": len(self.object_observations),
            "dynamic_observations": sum(item.is_dynamic for item in self.object_observations),
            "static_observations": sum(not item.is_dynamic for item in self.object_observations),
            "mean_confidence": float(np.mean(confidences)) if confidences else 0.0,
            "class_counts": dict(sorted(class_counts.items())),
        }
        with (output / "object_summary.json").open("w", encoding="utf-8") as handle:
            json.dump(object_summary, handle, indent=2)

        summary = {
            "raw_points": int(before),
            "downsampled_points": int(len(points_out)),
            "object_observations": len(self.object_observations),
            "processed_frames": len(self.frame_summaries),
            "object_summary": object_summary,
            **(metadata or {}),
        }
        with (output / "run_metadata.json").open("w", encoding="utf-8") as handle:
            json.dump(summary, handle, indent=2)
        return summary
