from __future__ import annotations

import argparse

import numpy as np

from semantic_slam.geometry import umeyama_rigid_alignment
from semantic_slam.io import load_tum_poses, nearest_pose


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate a TUM-format estimated trajectory.")
    parser.add_argument("--estimate", required=True)
    parser.add_argument("--ground-truth", required=True)
    parser.add_argument("--max-difference", type=float, default=0.02)
    args = parser.parse_args()

    estimated = load_tum_poses(args.estimate)
    ground_truth = load_tum_poses(args.ground_truth)

    est_positions = []
    gt_positions = []
    for pose in estimated:
        gt = nearest_pose(ground_truth, pose.timestamp, max_difference=args.max_difference)
        if gt is None:
            continue
        est_positions.append(pose.matrix[:3, 3])
        gt_positions.append(gt.matrix[:3, 3])

    est = np.asarray(est_positions, dtype=np.float64)
    gt = np.asarray(gt_positions, dtype=np.float64)
    if len(est) < 3:
        raise RuntimeError("Not enough timestamp-matched poses for evaluation")

    rotation, translation = umeyama_rigid_alignment(est, gt)
    aligned = (rotation @ est.T).T + translation
    errors = np.linalg.norm(aligned - gt, axis=1)

    print(f"Matched poses: {len(errors)}")
    print(f"ATE RMSE:      {np.sqrt(np.mean(errors ** 2)):.6f} m")
    print(f"ATE mean:      {np.mean(errors):.6f} m")
    print(f"ATE median:    {np.median(errors):.6f} m")
    print(f"ATE max:       {np.max(errors):.6f} m")


if __name__ == "__main__":
    main()
