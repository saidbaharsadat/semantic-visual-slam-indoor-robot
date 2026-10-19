# Experiment Log

| Date | Experiment | Pose source | Dynamic filter | Dataset | Map points | Notes |
|---|---|---|---|---|---:|---|
| 2026-10-01 | Ground-truth semantic map baseline (frame step 15) | TUM ground truth | Off | fr3/walking_xyz | 69,527 | 245,914 raw points; 319 semantic observations; 55 processed frames. |
| 2026-10-01 | Ground-truth filtered semantic map (frame step 15) | TUM ground truth | Person | fr3/walking_xyz | 44,550 | 177,824 raw points; 319 semantic observations; 71 person observations; 248 static observations; 27.69% raw-point reduction vs. unfiltered. |
| 2026-10-19 | Local ORB-SLAM3 RGB-D baseline | Estimated RGB-D poses | N/A | fr3/walking_xyz | N/A | Windows 11 WSL2; 826 timestamp-matched poses; rigid-aligned ATE RMSE 0.583068 m, mean 0.512931 m, median 0.447341 m, max 1.178976 m. |
| 2026-10-19 | Local SLAM-pose semantic map (frame step 15) | ORB-SLAM3 estimated poses | Off | fr3/walking_xyz | 119,869 | 251,323 raw points; 328 semantic observations; 56 processed frames; 73 person observations and 255 static observations. |
| 2026-10-19 | Local SLAM-pose filtered semantic map (frame step 15) | ORB-SLAM3 estimated poses | Person | fr3/walking_xyz | 94,213 | 181,231 raw points; same 56 frames and 328 observations; 70,092 raw points excluded (27.89% vs. unfiltered). |

### Provenance and limitations

The October 19 estimated-pose results were run locally on Ubuntu 22.04 in WSL2 and reported via terminal screenshots. The saved PLY files, model weights, full trajectory and result JSON remain on the local machine; this repository does not yet include the final visualization images or machine-readable run artifacts.

Point-count reduction measures dynamic-mask exclusion, **not** an improvement in pose-estimation accuracy or ground-truth map fidelity. The ORB-SLAM3 baseline has substantial ATE error. Before comparing SLAM-pose and ground-truth-pose maps spatially, align their coordinate frames and use comparable frame selection. Static-object viewpoint consistency and final map previews are pending.
