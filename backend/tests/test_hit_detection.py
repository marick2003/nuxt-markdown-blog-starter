from app.pipeline.features import FrameFeatures
from app.pipeline.hit_detection import detect_hits


def _features(speeds):
    return [FrameFeatures(t=i * 0.1, left_wrist_speed=0.0, right_wrist_speed=s) for i, s in enumerate(speeds)]


def test_detects_single_clear_peak():
    features = _features([0, 0.2, 0.5, 2.0, 0.6, 0.1, 0])
    hits = detect_hits(features, speed_threshold=1.0, refractory_seconds=0.3)
    assert len(hits) == 1
    assert hits[0].frame_index == 3
    assert hits[0].side == "RIGHT"


def test_merges_peaks_within_refractory_period():
    features = _features([0, 2.0, 1.8, 2.2, 0.1, 0])
    hits = detect_hits(features, speed_threshold=1.0, refractory_seconds=0.3)
    assert len(hits) == 1
    assert hits[0].frame_index == 3  # highest speed of the cluster wins


def test_separate_swings_outside_refractory_are_both_kept():
    features = _features([0, 2.0, 0, 0, 0, 2.0, 0])
    hits = detect_hits(features, speed_threshold=1.0, refractory_seconds=0.3)
    assert len(hits) == 2


def test_no_hits_below_threshold():
    features = _features([0, 0.3, 0.4, 0.2])
    hits = detect_hits(features, speed_threshold=1.0, refractory_seconds=0.3)
    assert hits == []


def test_none_frames_are_skipped():
    features = [None, None, FrameFeatures(t=0.2, left_wrist_speed=0, right_wrist_speed=2.0), None]
    hits = detect_hits(features, speed_threshold=1.0, refractory_seconds=0.3)
    assert len(hits) == 1
