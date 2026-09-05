from app.pipeline import analyze_frames


def _frame(right_wrist_x, right_wrist_y=0.5):
    return {
        "RIGHT_SHOULDER": (0.6, 0.3, 0.9),
        "LEFT_SHOULDER": (0.4, 0.3, 0.9),
        "RIGHT_ELBOW": (0.65, 0.4, 0.9),
        "LEFT_ELBOW": (0.35, 0.4, 0.9),
        "RIGHT_WRIST": (right_wrist_x, right_wrist_y, 0.9),
        "LEFT_WRIST": (0.3, 0.6, 0.9),
        "LEFT_HIP": (0.45, 0.6, 0.9),
        "RIGHT_HIP": (0.55, 0.6, 0.9),
    }


def test_analyze_frames_end_to_end_detects_one_forehand():
    # Right wrist stays put, swings out fast at index 4, then eases back.
    xs = [0.6, 0.6, 0.6, 0.6, 0.9, 0.65, 0.6, 0.6]
    frames = [_frame(x) for x in xs]
    timestamps = [i * 0.1 for i in range(len(xs))]

    stats, duration = analyze_frames(frames, timestamps)

    assert stats.rally_count == 1
    assert stats.shot_counts == {"forehand": 1}
    assert duration == timestamps[-1]


def test_analyze_frames_two_rallies_with_gap():
    xs = [0.6, 0.6, 0.9, 0.6, 0.6, 0.6, 0.6, 0.6, 0.9, 0.6]
    frames = [_frame(x) for x in xs]
    # Big timestamp gap between index 3 and index 8 to force a new rally.
    timestamps = [0.0, 0.1, 0.2, 0.3, 10.0, 10.1, 10.2, 10.3, 10.4, 10.5]

    stats, _duration = analyze_frames(frames, timestamps)

    assert stats.rally_count == 2
    assert sum(stats.shot_counts.values()) == 2


def test_analyze_frames_handles_missing_pose_gracefully():
    frames = [None, None, None]
    timestamps = [0.0, 0.1, 0.2]

    stats, duration = analyze_frames(frames, timestamps)

    assert stats.shots == []
    assert stats.rally_count == 0
    assert duration == 0.2
