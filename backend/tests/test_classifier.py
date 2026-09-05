from app.pipeline.classifier import (
    SHOT_BACKHAND,
    SHOT_FOREHAND,
    SHOT_SERVE,
    SHOT_UNKNOWN,
    classify_shot,
)


def _frame(right_wrist_x, right_wrist_y=0.5, shoulder_y=0.3):
    return {
        "RIGHT_SHOULDER": (0.6, shoulder_y, 0.9),
        "LEFT_SHOULDER": (0.4, shoulder_y, 0.9),
        "RIGHT_WRIST": (right_wrist_x, right_wrist_y, 0.9),
        "LEFT_WRIST": (0.3, 0.6, 0.9),
        "LEFT_HIP": (0.45, 0.6, 0.9),
        "RIGHT_HIP": (0.55, 0.6, 0.9),
    }


def test_forehand_when_wrist_stays_on_same_side():
    frame = _frame(right_wrist_x=0.7)  # right of torso midline (0.5)
    assert classify_shot(frame, side="RIGHT", is_first_hit_of_rally=False) == SHOT_FOREHAND


def test_backhand_when_wrist_crosses_midline():
    frame = _frame(right_wrist_x=0.3)  # crossed to the left of torso midline
    assert classify_shot(frame, side="RIGHT", is_first_hit_of_rally=False) == SHOT_BACKHAND


def test_serve_when_first_hit_and_contact_above_shoulder():
    frame = _frame(right_wrist_x=0.7, right_wrist_y=0.1, shoulder_y=0.3)  # smaller y = higher on screen
    assert classify_shot(frame, side="RIGHT", is_first_hit_of_rally=True) == SHOT_SERVE


def test_not_serve_when_high_contact_but_not_first_hit_of_rally():
    frame = _frame(right_wrist_x=0.7, right_wrist_y=0.1, shoulder_y=0.3)
    assert classify_shot(frame, side="RIGHT", is_first_hit_of_rally=False) == SHOT_FOREHAND


def test_unknown_when_landmarks_missing():
    frame = {"RIGHT_SHOULDER": (0.6, 0.3, 0.9)}
    assert classify_shot(frame, side="RIGHT", is_first_hit_of_rally=False) == SHOT_UNKNOWN
