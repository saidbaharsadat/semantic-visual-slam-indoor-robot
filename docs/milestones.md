# Implementation Milestones

## M0 — Repository and reproducibility
- Create GitHub repository.
- Add environment, configuration, documentation, and tests.
- Keep datasets, generated maps, and neural-network weights out of Git.

**Evidence:** repository builds cleanly and tests pass.

## M1 — RGB-D benchmark ingestion
- Download TUM `freiburg3_walking_xyz`.
- Associate RGB and depth timestamps.
- Load camera calibration and ground-truth poses.

**Evidence:** synchronized frame count and valid depth statistics.

## M2 — Object perception
- Run YOLO segmentation on RGB frames.
- Record class, confidence, masks, and bounding boxes.
- Visualize people and static indoor objects.

**Evidence:** annotated frames and detection summaries.

## M3 — Semantic 3D mapping with ground-truth poses
- Project depth pixels to 3D camera coordinates.
- Transform points into world coordinates.
- Estimate 3D centroids of detected instances.
- Build and save a semantic point cloud.

**Evidence:** `.ply` map and `object_observations.csv`.

## M4 — Dynamic-object filtering
- Treat `person` as dynamic.
- Remove dynamic-mask pixels before fusing geometry.
- Produce filtered and unfiltered maps.

**Evidence:** side-by-side qualitative comparison and map statistics.

## M5 — ORB-SLAM3 baseline
- Compile ORB-SLAM3.
- Run the RGB-D TUM example.
- Save `CameraTrajectory.txt`.
- Measure trajectory error against TUM ground truth.

**Evidence:** trajectory plot and ATE/RMSE.

## M6 — SLAM + semantic map integration
- Replace ground-truth poses with ORB-SLAM3 poses.
- Rebuild filtered and unfiltered semantic maps.
- Compare map quality and localization stability.

## M7 — Dynamic-aware SLAM front-end
- Reject visual features inside dynamic masks.
- Compare camera trajectory error with baseline ORB-SLAM3.

## M8 — Semantic consistency across viewpoints
- Associate repeated detections in 3D.
- Fuse repeated object observations.
- Track semantic landmark position variance.

## M9 — Live RGB-D camera
- Add a RealSense or another RGB-D sensor.
- Calibrate and run online mapping.
- Record a custom indoor sequence.

## M10 — Mobile robot integration
- Mount the RGB-D camera on a mobile base.
- Integrate pose/map data with ROS 2.
- Demonstrate indoor robotic perception while moving.
