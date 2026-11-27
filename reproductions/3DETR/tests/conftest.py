from pathlib import Path

import pytest


DEFAULT_SCENE = (
    Path(__file__).resolve().parents[3]
    / "data/raw/SUNRGBD/kv1/b3dodata/img_0063"
)


def pytest_addoption(parser):
    parser.addoption(
        "--scene-dir", type=Path, default=DEFAULT_SCENE,
        help="Path to a raw SUN RGB-D scene.",
    )


@pytest.fixture(scope="module")
def scene_dir(pytestconfig):
    """Provide the requested scene or the local SUN RGB-D sample."""
    path = pytestconfig.getoption("--scene-dir")
    if not path.is_dir():
        pytest.fail(f"SUN RGB-D scene missing at {path}. Set --scene-dir to a local scene.")
    return path
