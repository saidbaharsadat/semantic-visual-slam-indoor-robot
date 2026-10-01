from pathlib import Path

import numpy as np

from semantic_slam.pointcloud import voxel_downsample, write_ply


def test_voxel_downsample_averages_points_and_colors():
    points = np.array([
        [0.01, 0.01, 0.01],
        [0.02, 0.02, 0.02],
        [1.01, 1.01, 1.01],
    ])
    colors = np.array([
        [1.0, 0.0, 0.0],
        [0.0, 0.0, 1.0],
        [0.0, 1.0, 0.0],
    ])

    out_points, out_colors = voxel_downsample(points, colors, voxel_size=0.1)

    assert len(out_points) == 2
    np.testing.assert_allclose(out_points[0], [0.015, 0.015, 0.015])
    np.testing.assert_allclose(out_colors[0], [0.5, 0.0, 0.5])


def test_write_ply_creates_binary_ply(tmp_path: Path):
    path = tmp_path / "cloud.ply"
    write_ply(
        path,
        np.array([[1.0, 2.0, 3.0]], dtype=float),
        np.array([[1.0, 0.5, 0.0]], dtype=float),
    )

    raw = path.read_bytes()
    assert raw.startswith(b"ply\nformat binary_little_endian 1.0\n")
    assert b"element vertex 1\n" in raw
