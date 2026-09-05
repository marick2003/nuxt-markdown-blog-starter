from app.pipeline.hit_detection import HitEvent
from app.pipeline.stats import build_stats, segment_rallies


def test_segment_rallies_splits_on_long_gap():
    times = [0.0, 0.5, 1.0, 6.0, 6.5]
    assert segment_rallies(times, rally_gap_seconds=4.0) == [0, 0, 0, 1, 1]


def test_segment_rallies_empty():
    assert segment_rallies([], rally_gap_seconds=4.0) == []


def test_build_stats_counts_and_marks_first_hit_of_each_rally():
    hits = [
        HitEvent(t=0.0, frame_index=0, side="RIGHT", speed=2.0),
        HitEvent(t=0.5, frame_index=1, side="LEFT", speed=2.0),
        HitEvent(t=6.0, frame_index=2, side="RIGHT", speed=2.0),
    ]
    seen_first_flags = []

    def classify_fn(hit, is_first):
        seen_first_flags.append(is_first)
        return "forehand"

    stats = build_stats(hits, classify_fn, rally_gap_seconds=4.0)

    assert stats.rally_count == 2
    assert stats.shot_counts == {"forehand": 3}
    assert seen_first_flags == [True, False, True]
    assert [s.rally_index for s in stats.shots] == [0, 0, 1]
