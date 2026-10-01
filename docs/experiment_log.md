# Experiment Log

| Date | Experiment | Pose source | Dynamic filter | Dataset | ATE RMSE | Map points | Notes |
|---|---|---|---|---|---:|---:|---|
| TBD | Ground-truth semantic map baseline | TUM ground truth | Off | fr3/walking_xyz | N/A | TBD | Pipeline validation |
| 2026-10-01 | Ground-truth filtered semantic map (smoke test, frame step 90) | TUM ground truth | Person | fr3/walking_xyz | N/A | 16,396 | 827 RGB-depth pairs; 9 processed frames; 28,744 raw points; 56 object observations; 1 frame skipped for pose-time mismatch. GitHub Actions run 36845520089. |
| TBD | ORB-SLAM3 baseline | ORB-SLAM3 | Off | fr3/walking_xyz | TBD | TBD | Localization baseline |
| TBD | ORB-SLAM3 semantic map | ORB-SLAM3 | Person | fr3/walking_xyz | TBD | TBD | Integrated system |
