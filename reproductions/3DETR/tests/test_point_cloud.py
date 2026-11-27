import cv2
import numpy as np
import pytest

from src.dataset.loader import (
    get_scene_paths,
    load_depth,
    load_intrinsics,
    load_rgb,
    load_rtilt,
)
from src.dataset.preprocess import construct_point_cloud


@pytest.fixture(scope="module")
def paths(scene_dir):
    """Resolve the scene files once for all checks."""
    print(f"Scene {scene_dir}")
    return get_scene_paths(scene_dir)


@pytest.fixture(scope="module")
def camera_cloud(paths):
    """Build the unrotated cloud and track its source pixels."""
    rgb = load_rgb(paths["rgb"])
    depth = load_depth(paths["depth"])
    intrinsics = load_intrinsics(paths["intrinsics"])
    rows, cols = np.nonzero(depth > 0)
    assert rows.size > 0, "Scene has no positive depth pixels"
    points, colors = construct_point_cloud(depth, rgb, intrinsics, np.eye(3))
    return points, colors, rows, cols, depth[rows, cols], rgb, intrinsics


def test_load_rgb(paths):
    """Check RGB channel order, shape, and exact pixel values."""
    bgr = cv2.imread(str(paths["rgb"]), cv2.IMREAD_COLOR)
    assert bgr is not None, paths["rgb"]
    rgb = load_rgb(paths["rgb"])
    assert rgb.dtype == np.uint8
    np.testing.assert_array_equal(rgb, bgr[..., ::-1])


def test_load_depth(paths):
    """Check depth decoding in meters, including zero-depth pixels."""
    encoded = cv2.imread(str(paths["depth"]), cv2.IMREAD_UNCHANGED)
    assert encoded is not None, paths["depth"]
    assert encoded.ndim == 2 and encoded.dtype == np.uint16
    raw = encoded.astype(np.uint32)
    decoded = (raw // 8) + (raw % 8) * 8192
    expected = decoded.astype(np.float32) / 1000.0
    depth = load_depth(paths["depth"])
    assert depth.dtype == np.float32
    assert depth.shape == load_rgb(paths["rgb"]).shape[:2]
    np.testing.assert_array_equal(depth, expected)


def test_load_intrinsics(paths):
    """Check that K preserves the file values and camera matrix layout."""
    expected = np.loadtxt(paths["intrinsics"]).reshape(3, 3)
    intrinsics = load_intrinsics(paths["intrinsics"])
    np.testing.assert_array_equal(intrinsics, expected)
    assert np.isfinite(intrinsics).all()
    assert intrinsics[0, 0] > 0 and intrinsics[1, 1] > 0
    np.testing.assert_array_equal(intrinsics[2], [0, 0, 1])


def test_load_rtilt(paths):
    """Check that Rtilt preserves the on-disk rotation orientation."""
    expected = np.loadtxt(paths["extrinsics"])[:, :3]
    rtilt = load_rtilt(paths["extrinsics"])
    print(f"On-disk rotation\n{expected}\nLoaded rotation\n{rtilt}")
    print(f"Max difference from transpose: {np.max(np.abs(expected - expected.T)):.6g}")
    np.testing.assert_array_equal(rtilt, expected)


def test_camera_axis_order():
    """Check (X, Z, -Y) with a pixel whose camera position is known."""
    depth = np.array([[0, 0], [0, 4]], dtype=np.float32)
    rgb = np.zeros((2, 2, 3), dtype=np.uint8)
    intrinsics = np.array([[2, 0, 1], [0, 4, 1], [0, 0, 1]])
    points, _ = construct_point_cloud(depth, rgb, intrinsics, np.eye(3))
    np.testing.assert_array_equal(points, [[2, 4, -1]])


def test_one_based_pixel_indexing(camera_cloud):
    """Reproject every camera point to its one-based MATLAB pixel."""
    points, colors, rows, cols, z, rgb, intrinsics = camera_cloud
    np.testing.assert_array_equal(points[:, 1], z)
    np.testing.assert_array_equal(colors, rgb[rows, cols])
    u = points[:, 0] / z * intrinsics[0, 0] + intrinsics[0, 2]
    v = -points[:, 2] / z * intrinsics[1, 1] + intrinsics[1, 2]
    sample = len(rows) // 2
    print(f"Sample (row, col) = ({rows[sample]}, {cols[sample]})")
    print(f"Reprojected (u, v) = ({u[sample]:.6f}, {v[sample]:.6f})")
    np.testing.assert_allclose(u, cols + 1, rtol=0, atol=1e-8)
    np.testing.assert_allclose(v, rows + 1, rtol=0, atol=1e-8)


def test_gravity_alignment(paths, camera_cloud):
    """Compare the rotated cloud with MATLAB's column-vector transform."""
    camera_points, _, _, _, _, rgb, intrinsics = camera_cloud
    depth = load_depth(paths["depth"])
    rtilt = load_rtilt(paths["extrinsics"])
    points, _ = construct_point_cloud(depth, rgb, intrinsics, rtilt)
    file_rotation = np.loadtxt(paths["extrinsics"])[:, :3]
    expected = (file_rotation @ camera_points.T).T
    print(f"Max rotation error across {len(points):,} points: "
          f"{np.max(np.abs(points - expected)):.6g} m")
    np.testing.assert_allclose(points, expected, rtol=0, atol=1e-8)

