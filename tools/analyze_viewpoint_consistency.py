from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import numpy as np

from semantic_slam.consistency import cluster_observations, summarize_cluster


def load_static_observations(path: Path):
    observations = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        for row in csv.DictReader(handle):
            if int(row["is_dynamic"]):
                continue
            observations.append(
                (
                    float(row["timestamp"]),
                    row["class"],
                    np.array([float(row["x"]), float(row["y"]), float(row["z"])]),
                )
            )
    return observations


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Measure simple spatial consistency of repeated static semantic observations."
    )
    parser.add_argument("--observations", required=True)
    parser.add_argument("--output-json", required=True)
    parser.add_argument("--radius", type=float, default=0.6)
    parser.add_argument("--min-observations", type=int, default=3)
    args = parser.parse_args()

    observations = load_static_observations(Path(args.observations))
    clusters = cluster_observations(observations, radius_m=args.radius)
    summaries = [
        summarize_cluster(cluster)
        for cluster in clusters
        if len(cluster.points) >= args.min_observations
    ]

    summaries.sort(key=lambda item: (-item["observations"], item["class_name"]))
    weighted_count = sum(item["observations"] for item in summaries)
    weighted_mean = (
        sum(item["mean_position_deviation_m"] * item["observations"] for item in summaries)
        / weighted_count
        if weighted_count
        else 0.0
    )

    result = {
        "method": "same-class spatial clustering",
        "cluster_radius_m": args.radius,
        "minimum_observations_per_cluster": args.min_observations,
        "static_observations": len(observations),
        "repeated_static_clusters": len(summaries),
        "observations_in_repeated_clusters": weighted_count,
        "weighted_mean_position_deviation_m": weighted_mean,
        "clusters": summaries,
    }

    output = Path(args.output_json)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
