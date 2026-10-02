# Semantic Visual SLAM for Indoor Mobile Robot Perception

An ongoing robotic-vision prototype for RGB-D object perception, semantic 3D mapping, and basic dynamic-object filtering. The current implementation validates the semantic-mapping pipeline with benchmark camera poses; full Visual SLAM integration is planned as future work.

## Project goals

This project explores how RGB-D perception can be used to build a simple semantic representation of an indoor environment.

The current work focuses on:

- detecting and segmenting objects in RGB frames;
- using aligned depth to estimate their 3D positions;
- transforming observations into a common world coordinate frame;
- building a semantic point-cloud representation of the scene;
- reducing dynamic-scene artifacts by filtering people from the stable map;
- comparing filtered and unfiltered reconstructions;
- preparing the system for later integration with Visual SLAM-based camera poses.

## Current project stage

The current prototype uses the TUM RGB-D `freiburg3_walking_xyz` sequence to study object perception, 3D semantic mapping, and person filtering with benchmark camera poses. Visual SLAM pose integration, live-camera experiments, and mobile-robot deployment remain future extensions as the project develops.

## Pipeline

```text
RGB-D frames
   |
   +--> Object segmentation ----> semantic masks
   |
   +--> Visual SLAM ------------> camera poses
                                  |
depth + masks + camera poses -----+
                 |
                 v
        3D back-projection
                 |
                 v
       world-frame fusion
                 |
        +--------+--------+
        |                 |
        v                 v
 stable map        semantic objects
(dynamic pixels     class + 3D
 removed)           position
        |                 |
        +--------+--------+
                 v
             evaluation
```

## Technology stack

- Ultralytics YOLO segmentation for object perception
- NumPy/OpenCV for RGB-D geometry and point-cloud export
- OpenCV and NumPy for RGB-D processing and geometry
- TUM RGB-D benchmark for reproducible evaluation

ORB-SLAM3 is an external dependency and is not vendored into this repository.

## Repository layout

```text
configs/                 experiment configuration
data/                    local datasets (ignored by Git)
docs/                    milestones and experiment log
results/                 generated outputs (ignored by Git)
src/semantic_slam/       reusable Python package
tests/                   unit tests
tools/                   command-line experiment scripts
```

## Stage 1: validate semantic mapping

### 1. Create an environment

Python 3.10+ is recommended.

```bash
python -m venv .venv
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Windows PowerShell:

```powershell
.venv\Scripts\Activate.ps1
```

Install:

```bash
pip install -e .
```

### 2. Add the TUM RGB-D sequence

Extract `rgbd_dataset_freiburg3_walking_xyz` under:

```text
data/rgbd_dataset_freiburg3_walking_xyz/
```

The folder should contain `rgb.txt`, `depth.txt`, `groundtruth.txt`, `rgb/`, and `depth/`.

### 3. Create RGB-depth associations

```bash
python tools/make_associations.py \
  --rgb data/rgbd_dataset_freiburg3_walking_xyz/rgb.txt \
  --depth data/rgbd_dataset_freiburg3_walking_xyz/depth.txt \
  --output data/rgbd_dataset_freiburg3_walking_xyz/associations.txt
```

### 4. Build the first semantic map with ground-truth poses

```bash
python tools/build_semantic_map.py \
  --config configs/tum_fr3_walking.yaml \
  --dataset data/rgbd_dataset_freiburg3_walking_xyz \
  --poses data/rgbd_dataset_freiburg3_walking_xyz/groundtruth.txt \
  --output results/groundtruth_map \
  --filter-dynamic
```

Expected outputs include:

```text
semantic_map.ply
object_observations.csv
frame_summary.csv
run_metadata.json
```

Run the same command without `--filter-dynamic` to create an unfiltered comparison map.

## Planned next stage: Visual SLAM integration

A later milestone will replace benchmark poses with an estimated RGB-D Visual SLAM trajectory and evaluate localization error. This is intentionally listed as future work rather than part of the current completed prototype.

## First benchmark result

A reproducible filtered-vs-unfiltered smoke experiment has now completed on the TUM RGB-D `freiburg3_walking_xyz` sequence using TUM ground-truth poses and a frame step of 90.

| Metric | Unfiltered | Person-filtered |
| --- | ---: | ---: |
| Processed frames | 9 | 9 |
| 3D object observations | 56 | 56 |
| Raw map points | 37,262 | 28,744 |
| Voxel-downsampled points | 20,998 | 16,396 |

Dynamic-person filtering removed **8,518 raw 3D points (22.86%)** from the sampled reconstruction while preserving the same 56 semantic object observations.

### Unfiltered semantic map

![Top-down unfiltered semantic map](docs/images/tum_unfiltered_topdown.png)

### Person-filtered semantic map

![Top-down person-filtered semantic map](docs/images/tum_filtered_topdown.png)

The figures above are generated automatically from the actual binary PLY outputs by `tools/render_map_preview.py`. The full filtered/unfiltered maps, CSV observations, metadata, and comparison JSON are produced by the GitHub Actions benchmark workflow.

## Research evidence we will add

- annotated detection frames;
- filtered vs unfiltered semantic maps;
- trajectory plots;
- ATE/RMSE tables;
- object observation statistics;
- viewpoint-consistency analysis;
- a live RGB-D demo;
- later, ROS 2/mobile-robot integration.

See `docs/milestones.md` for the implementation roadmap.
