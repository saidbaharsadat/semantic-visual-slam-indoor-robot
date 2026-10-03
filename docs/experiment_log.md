# Experiment Log

| Date | Experiment | Pose source | Dynamic filter | Dataset | Map points | Notes |
|---|---|---|---|---|---:|---|
| 2026-10-01 | Ground-truth semantic map baseline (frame step 15) | TUM ground truth | Off | fr3/walking_xyz | 69,527 | 245,914 raw points; 319 semantic observations; 55 processed frames. |
| 2026-10-01 | Ground-truth filtered semantic map (frame step 15) | TUM ground truth | Person | fr3/walking_xyz | 44,550 | 177,824 raw points; 319 semantic observations; 71 person observations; 248 static observations; 27.69% raw-point reduction vs. unfiltered. |
| Future | ORB-SLAM3 baseline | Estimated RGB-D pose | Off | fr3/walking_xyz | TBD | Planned Visual SLAM pose-integration experiment. |
| Future | ORB-SLAM3 semantic map | Estimated RGB-D pose | Person | fr3/walking_xyz | TBD | Planned comparison against the current benchmark-pose semantic map. |
