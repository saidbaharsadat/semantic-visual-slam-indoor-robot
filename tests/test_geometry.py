import numpy as np

from semantic_slam.geometry import (
    depth_pixels_to_camera_points,
    transform_points,
    umeyama_rigid_alignment,
)
from semantic_slam.io import quaternion_xyzw_to_rotation


def test_backprojection_center_pixel():
    points = depth_pixels_to_camera_points(
        np.array([320]), np.array([240]), np.array([2.0]),
        fx=500, fy=500, cx=320, cy=240,
    )
    np.testing.assert_allclose(points[0], [0.0, 0.0, 2.0])


def test_transform_points_translation():
    transform = np.eye(4)
    transform[:3, 3] = [1, 2, 3]
    result = transform_points(np.array([[0.5, 0.5, 0.5]]), transform)
    np.testing.assert_allclose(result[0], [1.5, 2.5, 3.5])


def test_identity_quaternion():
    rotation = quaternion_xyzw_to_rotation(0, 0, 0, 1)
    np.testing.assert_allclose(rotation, np.eye(3))


def test_umeyama_rigid_alignment():
    source = np.array([[0,0,0],[1,0,0],[0,1,0],[0,0,1]], dtype=float)
    angle = np.deg2rad(30)
    rotation_true = np.array([
        [np.cos(angle), -np.sin(angle), 0],
        [np.sin(angle), np.cos(angle), 0],
        [0, 0, 1],
    ])
    translation_true = np.array([1.0, -2.0, 0.5])
    target = (rotation_true @ source.T).T + translation_true

    rotation, translation = umeyama_rigid_alignment(source, target)
    aligned = (rotation @ source.T).T + translation
    np.testing.assert_allclose(aligned, target, atol=1e-8)
