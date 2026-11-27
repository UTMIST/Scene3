"""
preprocess.py

Functions for preprocessing a single raw SUN RGB-D scene into
a standardized representation suitable for model training.
"""

from argparse import ArgumentParser
from pathlib import Path
import numpy as np
from itertools import islice

# Data loading
from .loader import (
    load_rgb,
    load_depth,
    load_intrinsics,
    load_rtilt,
    get_scene_paths,
)

# Processed data writing
# from .writer import (
#     save_processed,
# )

# Visualization (optional, for debugging)
from .visualize import (
    visualize_point_cloud,
)

# Utilities
# from ..utils.logger import (
#     get_logger,
# )


# HELPER: convert depth image to point cloud 3D coordinates
def construct_point_cloud(depth, rgb, intrinsics, Rtilt):

    # use the provided sensor intrinsics 
    fx = intrinsics[0, 0]
    fy = intrinsics[1, 1]
    cx = intrinsics[0, 2]
    cy = intrinsics[1, 2]

    H, W = depth.shape
    # SUN RGB-D's MATLAB toolbox uses one-based pixel coordinates with K.
    u, v = np.meshgrid(np.arange(1, W + 1), np.arange(1, H + 1))

    # element-wise arithmetics to compute 3D coordinates
    Z = depth
    X = (u - cx) * Z / fx
    Y = (v - cy) * Z / fy

    # Construct point cloud in camera coordinates
    points = np.stack((X, Z, -Y), axis=-1)

    # Keep only pixels with valid depth
    valid = Z > 0
    points = points[valid]

    # Rotate into gravity-aligned coordinate system
    points = points @ Rtilt.T

    # apply valid mask to rgb 
    if rgb.shape[:2] != depth.shape:
        raise ValueError(
            f"RGB image shape {rgb.shape[:2]} does not match depth image shape {depth.shape}."
        )

    return points, rgb[valid]


# ---------------------------------------------------------------------
# MAIN SUN RGB-D PREPROCESSING ROUTINE
# ---------------------------------------------------------------------
def main():

    # Construct path to Scene3 repository root
    project_root = Path(__file__).resolve().parents[4]

    # Construct path to raw SUN RGB-D dataset
    dataset_root = project_root / "data" / "raw" / "SUNRGBD"

    # Paths to sensor folders to process
    sensor_roots = [
        dataset_root / "kv1" / "b3dodata",
        dataset_root / "kv1" / "NYUdata",
        dataset_root / "kv2" / "align_kv2",
        dataset_root / "kv2" / "kinect2data",
        dataset_root / "realsense" / "lg",
        dataset_root / "realsense" / "sa",
        dataset_root / "realsense" / "sh",
        dataset_root / "realsense" / "shr",
        # dataset_root / "xtion" / "sun3ddata",  # TODO: different path gen logic needed for sun3ddata
        dataset_root / "xtion" / "xtion_align_data",
    ]

    START_SCENE = 0
    NUM_SCENES = 2

    for sensor_root in sensor_roots:

        if not sensor_root.exists():
            print(f"Missing: {sensor_root}")
            continue

        scene_dirs = [
            d for d in sorted(sensor_root.iterdir())
            if d.is_dir()
        ]
        num_available = len(scene_dirs)

        if not (0 <= START_SCENE < START_SCENE + NUM_SCENES <= num_available):
            raise IndexError(
                f"Requested scene range [{START_SCENE}, {START_SCENE + NUM_SCENES - 1}] "
                f"is out of bounds. Valid range is [0, {num_available - 1}]."
            )

        for scene_dir in scene_dirs[START_SCENE:START_SCENE + NUM_SCENES]:

            paths = get_scene_paths(scene_dir)

            rgb = load_rgb(paths["rgb"])
            depth = load_depth(paths["depth"])
            intrinsics = load_intrinsics(paths["intrinsics"])
            rtilt = load_rtilt(paths["extrinsics"])

            points, colors = construct_point_cloud(
                depth,
                rgb,
                intrinsics,
                rtilt,
            )

            visualize_point_cloud(
                points,
                colors,
                window_name=paths["scene"],
            )


if __name__ == "__main__":
    parser = ArgumentParser(description="Preprocess SUN RGB-D point clouds.")
    parser.add_argument("--verify", type=Path, metavar="SCENE_DIR",
                        help="Check one scene's geometry without opening a viewer.")
    args = parser.parse_args()
    if args.verify is None:
        main()
    else:
        from tests import run_point_cloud_tests

        raise SystemExit(run_point_cloud_tests(args.verify))
