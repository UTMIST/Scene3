from pathlib import Path


def run_point_cloud_tests(scene_dir: Path) -> int:
    """Run all point-cloud checks and return pytest's exit code."""
    import pytest

    test_file = Path(__file__).with_name("test_point_cloud.py")
    return pytest.main(["-v", "-s", str(test_file), "--scene-dir", str(scene_dir)])
