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


def render_detection_preview(image_bgr, detections):
    preview = image_bgr.copy()
    overlay = preview.copy()

    for detection in detections:
        x1, y1, x2, y2 = map(int, detection.xyxy)
        is_dynamic = detection.class_name == "person"
        color = (0, 0, 255) if is_dynamic else (0, 180, 0)

        overlay[detection.mask] = color
        cv2.rectangle(preview, (x1, y1), (x2, y2), color, 2)
        label = f"{detection.class_name} {detection.confidence:.2f}"
        cv2.putText(
            preview,
            label,
            (x1, max(20, y1 - 6)),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            color,
            1,
            cv2.LINE_AA,
        )

    preview = cv2.addWeighted(overlay, 0.28, preview, 0.72, 0)
    return preview


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a semantic RGB-D map from TUM-style data.")
    parser.add_argument("--config", required=True)
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--poses", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--filter-dynamic", action="store_true")
    parser.add_argument("--frame-step", type=int, default=None)
    parser.add_argument(
        "--preview-count",
        type=int,
        default=0,
        help="Save annotated previews for the first N processed frames.",
    )
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
    preview_dir = output / "previews"

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

        if args.preview_count > 0 and used < args.preview_count:
            preview_dir.mkdir(parents=True, exist_ok=True)
            preview = render_detection_preview(image, detections)
            cv2.imwrite(str(preview_dir / f"frame_{used + 1:03d}.jpg"), preview)

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
        "preview_count": min(used, max(args.preview_count, 0)),
    }
    summary = mapper.save(output, metadata=metadata)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
