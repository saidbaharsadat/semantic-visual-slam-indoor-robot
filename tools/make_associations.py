from __future__ import annotations

import argparse
from pathlib import Path

from semantic_slam.io import associate_timestamped_paths, load_timestamped_paths


def main() -> None:
    parser = argparse.ArgumentParser(description="Associate TUM RGB and depth timestamps.")
    parser.add_argument("--rgb", required=True)
    parser.add_argument("--depth", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--max-difference", type=float, default=0.02)
    args = parser.parse_args()

    rgb = load_timestamped_paths(args.rgb)
    depth = load_timestamped_paths(args.depth)
    matches = associate_timestamped_paths(rgb, depth, args.max_difference)

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8") as handle:
        handle.write("# rgb_timestamp rgb_path depth_timestamp depth_path\n")
        for row in matches:
            handle.write(
                f"{row.rgb_timestamp:.6f} {row.rgb_path} "
                f"{row.depth_timestamp:.6f} {row.depth_path}\n"
            )

    print(f"Associated {len(matches)} RGB-depth pairs -> {output}")


if __name__ == "__main__":
    main()
