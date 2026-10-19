from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


PLY_DTYPE = np.dtype(
    [
        ("x", "<f4"),
        ("y", "<f4"),
        ("z", "<f4"),
        ("red", "u1"),
        ("green", "u1"),
        ("blue", "u1"),
    ]
)


def read_binary_ply(path: str | Path) -> tuple[np.ndarray, np.ndarray]:
    path = Path(path)
    with path.open("rb") as handle:
        header = []
        while True:
            line = handle.readline()
            if not line:
                raise RuntimeError(f"Unexpected end of PLY header: {path}")
            decoded = line.decode("ascii").strip()
            header.append(decoded)
            if decoded == "end_header":
                break

        if "format binary_little_endian 1.0" not in header:
            raise ValueError("This preview tool expects binary little-endian PLY files")

        vertex_line = next(line for line in header if line.startswith("element vertex "))
        count = int(vertex_line.split()[-1])
        vertices = np.fromfile(handle, dtype=PLY_DTYPE, count=count)

    points = np.column_stack((vertices["x"], vertices["y"], vertices["z"])).astype(np.float64)
    colors = (
        np.column_stack((vertices["red"], vertices["green"], vertices["blue"])).astype(np.float64)
        / 255.0
    )
    return points, colors


def main() -> None:
    parser = argparse.ArgumentParser(description="Render a top-down PNG preview from a semantic-map PLY.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--max-points", type=int, default=25000)
    parser.add_argument(
        "--xlim", nargs=2, type=float, metavar=("MIN_X", "MAX_X"),
        help="Optional fixed World X limits in meters for fair map comparisons.",
    )
    parser.add_argument(
        "--zlim", nargs=2, type=float, metavar=("MIN_Z", "MAX_Z"),
        help="Optional fixed World Z limits in meters for fair map comparisons.",
    )
    args = parser.parse_args()
    if args.xlim is not None and args.xlim[0] >= args.xlim[1]:
        parser.error("--xlim requires MIN_X < MAX_X")
    if args.zlim is not None and args.zlim[0] >= args.zlim[1]:
        parser.error("--zlim requires MIN_Z < MAX_Z")

    points, colors = read_binary_ply(args.input)
    if len(points) > args.max_points:
        indices = np.linspace(0, len(points) - 1, args.max_points, dtype=int)
        points = points[indices]
        colors = colors[indices]

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(8, 6), dpi=180)
    ax.scatter(points[:, 0], points[:, 2], c=colors, s=2, linewidths=0)
    ax.set_xlabel("World X (m)")
    ax.set_ylabel("World Z (m)")
    ax.set_title(args.title)
    ax.set_aspect("equal", adjustable="box")
    if args.xlim is not None:
        ax.set_xlim(*args.xlim)
    if args.zlim is not None:
        ax.set_ylim(*args.zlim)
    ax.grid(True, alpha=0.2)
    fig.tight_layout()
    fig.savefig(output, bbox_inches="tight")
    plt.close(fig)


if __name__ == "__main__":
    main()
