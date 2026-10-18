import numpy as np

from semantic_slam.consistency import cluster_observations, summarize_cluster


def test_cluster_observations_groups_nearby_same_class_points():
    observations = [
        (0.0, "chair", np.array([0.0, 0.0, 0.0])),
        (1.0, "chair", np.array([0.1, 0.0, 0.0])),
        (2.0, "chair", np.array([2.0, 0.0, 0.0])),
        (3.0, "tv", np.array([0.05, 0.0, 0.0])),
    ]

    clusters = cluster_observations(observations, radius_m=0.5)

    chair_clusters = [cluster for cluster in clusters if cluster.class_name == "chair"]
    tv_clusters = [cluster for cluster in clusters if cluster.class_name == "tv"]

    assert sorted(len(cluster.points) for cluster in chair_clusters) == [1, 2]
    assert len(tv_clusters) == 1


def test_summarize_cluster_reports_small_spread():
    observations = [
        (0.0, "chair", np.array([1.0, 2.0, 3.0])),
        (1.0, "chair", np.array([1.1, 2.0, 3.0])),
        (2.0, "chair", np.array([0.9, 2.0, 3.0])),
    ]
    cluster = cluster_observations(observations, radius_m=0.5)[0]
    summary = summarize_cluster(cluster)

    assert summary["observations"] == 3
    assert summary["class_name"] == "chair"
    assert summary["mean_position_deviation_m"] < 0.1
    assert summary["time_span_s"] == 2.0
