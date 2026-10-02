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
   +--> Camera poses
        current: TUM ground truth
        planned: Visual SLAM
                 |
depth + masks + camera poses
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
        qualitative + quantitative
              evaluation
```

## Tools and software used so far

| Tool / software | Current use |
| --- | --- |
| **Python** | Main implementation language for the perception and mapping pipeline |
| **Ultralytics YOLO segmentation** | Object and person detection/segmentation in RGB frames |
| **OpenCV** | RGB-D image loading, image processing, masks, and annotated detection previews |
| **NumPy** | Camera geometry, 3D back-projection, coordinate transformations, and point-cloud processing |
| **PyYAML** | Experiment and camera configuration |
| **Matplotlib** | Rendering point-cloud result previews for comparison |
| **pytest** | Unit testing for geometry and point-cloud utilities |
| **Git / GitHub** | Version control, experiment tracking, documentation, and project management |
| **GitHub Actions** | Reproducible testing and benchmark execution |
| **TUM RGB-D Dataset** | Current indoor RGB-D benchmark, including synchronized RGB, depth, and ground-truth camera poses |

### Simulation status

No robotics simulator has been used in the current experiments. The present stage is **dataset-based**, using the TUM RGB-D benchmark to validate the semantic perception and mapping components before moving to simulated or physical robot experiments.

## Planned tools and simulation software

| Tool / software | Planned use |
| --- | --- |
| **ORB-SLAM3** | Replace benchmark ground-truth poses with estimated RGB-D camera poses |
| **ROS 2** | Connect perception, camera pose, mapping, and later robot components as separate nodes |
| **Gazebo Sim** | Create a simple indoor mobile-robot simulation before physical deployment |
| **RViz2** | Visualize camera poses, point clouds, semantic observations, and robot data |
| **Intel RealSense / RealSense SDK** | Future live RGB-D experiments with a physical depth camera |
| **Mobile robot platform** | Later validation of the perception pipeline while the robot moves in an indoor environment |

These tools are planned extensions; they are not presented as part of the current completed prototype.

## Future work

The next development steps are intentionally incremental:

1. **Improve current semantic-mapping experiments** by testing more frames and presenting additional annotated object-detection examples.
2. **Study viewpoint consistency** by checking how the estimated 3D position of selected static objects changes across different observations.
3. **Integrate Visual SLAM poses** using ORB-SLAM3 and perform a basic comparison against the current benchmark-pose version.
4. **Test live RGB-D input** using a depth camera such as Intel RealSense.
5. **Build a simple ROS 2 + Gazebo Sim experiment** to connect perception, mapping, and a simulated indoor mobile robot.
6. **Move to a physical mobile robot** only after the perception and pose-integration stages are stable.

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

## Current benchmark result

A stronger filtered-vs-unfiltered experiment has been completed on the TUM RGB-D `freiburg3_walking_xyz` sequence using TUM ground-truth poses and a frame step of 15.

| Metric | Unfiltered | Person-filtered |
| --- | ---: | ---: |
| Processed frames | 55 | 55 |
| Semantic object observations | 319 | 319 |
| Raw map points | 245,914 | 177,824 |
| Voxel-downsampled points | 69,527 | 44,550 |

The current run produced **319 semantic observations** across the sampled frames, including **71 person observations** and **248 static-object observations**, with a mean detection confidence of approximately **0.714**.

Dynamic-person filtering removed **68,090 raw 3D points (27.69%)** from the sampled reconstruction while keeping the semantic observation records available for analysis.

### Unfiltered semantic map

![Top-down unfiltered semantic map](docs/images/tum_unfiltered_topdown.png)

### Person-filtered semantic map

![Top-down person-filtered semantic map](docs/images/tum_filtered_topdown.png)

The figures above are generated automatically from the actual binary PLY outputs by `tools/render_map_preview.py`. The full filtered/unfiltered maps, CSV observations, metadata, and comparison JSON are produced by the GitHub Actions benchmark workflow.

## Current evidence

- synchronized RGB-D benchmark processing;
- YOLO object/person segmentation;
- depth-based 3D object localization;
- semantic point-cloud generation;
- filtered vs. unfiltered reconstruction comparison;
- semantic observation statistics;
- annotated detection previews;
- reproducible benchmark workflow.

See `docs/milestones.md` for the implementation roadmap and the separation between current work and future extensions.
