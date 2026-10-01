from __future__ import annotations

import argparse
import json
from pathlib import Path

import cv2
import yaml
from tqdm import tqdm

from semantic_slam.detector import YoloSegmenter
from semantic_slam.io import (
    associate_timestamped_paths,
    load_associations,
    load_timestamped_paths,
    load_tum_poses,
    nearest_pose,
)
from semantic_slam.mapper import SemanticMapper


def load_or_create_associations(dataset: Path):
    association_file = dataset / "associations.txt"
    if association_file.exists():
        return load_associations(association_file)
    rgb = load_timestamped_paths(dataset / "rgb.txt")
    depth = load_timestamped_paths(dataset / "depth.txt")
    return associate_timestamped_paths(rgb, depth, max_difference=0.02)


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a semantic RGB-D map from TUM-style data.")
    parser.add_argument("--config", required=True)
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--poses", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--filter-dynamic", action="store_true")
    parser.add_argument("--frame-step", type=int, default=None)
    args = parser.parse_args()

    config_path = Path(args.config)
    dataset = Path(args.dataset)
    output = Path(args.output)

    with config_path.open("r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle)

    associations = load_or_create_associations(dataset)
    poses = load_tum_poses(args.poses)
    if not associations:
        raise RuntimeError("No RGB-depth associations found")
    if not poses:
        raise RuntimeError("No poses found")

    detector_cfg = config["detector"]
    detector = YoloSegmenter(
        model_name=detector_cfg.get("model", "yolo26n-seg.pt"),
        confidence=float(detector_cfg.get("confidence", 0.35)),
        iou=float(detector_cfg.get("iou", 0.55)),
        device=detector_cfg.get("device", "auto"),
    )
    mapper = SemanticMapper(config)

    frame_step = args.frame_step or int(config["mapping"].get("frame_step", 10))
    max_pose_dt = float(config["mapping"].get("max_pose_time_difference_s", 0.04))

    used = skipped_pose = skipped_image = 0

    for association in tqdm(associations[::frame_step], desc="Building semantic map"):
        pose = nearest_pose(poses, association.rgb_timestamp, max_difference=max_pose_dt)
        if pose is None:
            skipped_pose += 1
            continue

        image = cv2.imread(str(dataset / association.rgb_path), cv2.IMREAD_COLOR)
        depth = cv2.imread(str(dataset / association.depth_path), cv2.IMREAD_UNCHANGED)
        if image is None or depth is None:
            skipped_image += 1
            continue

        detections = detector(image)
        mapper.process_frame(
            timestamp=association.rgb_timestamp,
            image_bgr=image,
            depth_raw=depth,
            twc=pose.matrix,
            detections=detections,
            filter_dynamic=args.filter_dynamic,
        )
        used += 1

    metadata = {
        "config": str(config_path),
        "dataset": str(dataset),
        "poses": str(args.poses),
        "filter_dynamic": bool(args.filter_dynamic),
        "frame_step": frame_step,
        "used_frames": used,
        "skipped_no_pose": skipped_pose,
        "skipped_image": skipped_image,
    }
    summary = mapper.save(output, metadata=metadata)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
