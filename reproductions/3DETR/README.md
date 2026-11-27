# 3DETR Reproduction

This directory contains our reproduction and experimentation work for **3DETR (3D Detection Transformer)**, a transformer-based model for 3D object detection from point clouds.

## Directory Structure

```text
reproductions/3DETR/
├── src/
│   └── dataset/
│       ├── loader.py       # Load RGB, depth, and camera parameters
│       ├── preprocess.py   # Construct and visualize point clouds
│       ├── writer.py       # Save processed data
│       └── visualize.py    # Point cloud visualization
├── notebooks/              # Exploratory notebooks
├── requirements.txt        # Python dependencies
└── README.md
```

The raw datasets are stored separately in the Scene³ repository to avoid duplication:

```text
Scene3/
└── data/
    ├── raw/
    │   └── SUNRGBD/
    └── processed/
```

## Getting Started

### 1. Navigate to the Reproduction Directory

From the Scene³ repository root:

```bash
cd reproductions/3DETR
```

### 2. Create and Activate a Virtual Environment

**macOS / Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows (PowerShell):**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install Dependencies

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

### 4. Prepare the Dataset

Download and extract the SUN RGB-D dataset into the shared data directory:

```text
Scene3/data/raw/SUNRGBD/
```

The expected structure includes:

```text
SUNRGBD/
├── kv1/
│   ├── b3dodata/
│   └── NYUdata/
├── kv2/
├── realsense/
└── xtion/
```

The preprocessing script expects the dataset at this location relative to the repository root.

## Running the Demo

The current demo loads RGB images, depth maps, camera intrinsics, and extrinsics from SUN RGB-D, constructs colored 3D point clouds, and displays them using Open3D.

From `reproductions/3DETR/`, with the virtual environment activated:

```bash
python -m src.dataset.preprocess
```

To adjust the number of scenes processed, modify these parameters inside `src/dataset/preprocess.py`:

```python
START_SCENE = 0
NUM_SCENES = 2
```

The script processes the selected number of scenes from each available sensor directory.

**Note:** Run the script using `python -m`, not `python src/dataset/preprocess.py`, because the package uses relative imports.

## Running the Tests

The tests verify that the SUN RGB-D loader reads RGB, depth, intrinsics, and `Rtilt` correctly. They also check that point-cloud geometry follows the MATLAB toolbox’s one-based pixel indexing, `(X, Z, -Y)` axis order, and gravity alignment.

From `reproductions/3DETR/`, activate the virtual environment and install the dependencies with `python -m pip install -r requirements.txt`. Then run the point-cloud tests.

```bash
python -m pytest -v -s tests
```

`-v` lists each test and its result. `-s` shows the verification logs.

The tests use the local SUN RGB-D scene `kv1/b3dodata/img_0063` by default. To check another scene, pass the path to its folder.

```bash
python -m pytest -v -s tests --scene-dir /path/to/scene
```
