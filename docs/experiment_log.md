# Experiment Log

| Date | Experiment | Pose source | Dynamic filter | Dataset | ATE RMSE | Map points | Notes |
|---|---|---|---|---|---:|---:|---|
| 2026-10-01 | Ground-truth semantic map baseline (smoke test, frame step 90) | TUM ground truth | Off | fr3/walking_xyz | N/A | 20,998 | 37,262 raw points; 56 object observations; 9 processed frames. GitHub Actions run 36846098659. |
| 2026-10-01 | Ground-truth filtered semantic map (smoke test, frame step 90) | TUM ground truth | Person | fr3/walking_xyz | N/A | 16,396 | 28,744 raw points; 56 object observations; 9 processed frames. Dynamic filtering removed 8,518 raw points (22.86%) vs unfiltered. GitHub Actions run 36846098659. |
| TBD | ORB-SLAM3 baseline | ORB-SLAM3 | Off | fr3/walking_xyz | TBD | TBD | Localization baseline |
| TBD | ORB-SLAM3 semantic map | ORB-SLAM3 | Person | fr3/walking_xyz | TBD | TBD | Integrated system |
