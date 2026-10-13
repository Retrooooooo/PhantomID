from phantomid.capture import Accumulator


def test_keyboard_features_are_aggregate_and_windows_do_not_reuse_samples():
    accumulator = Accumulator()
    for i in range(6):
        accumulator.press("secret", i * 0.1)
        accumulator.release("secret", i * 0.1 + 0.05)
    features = accumulator.window()
    assert abs(features["key_dwell"] - 0.05) < 0.0001
    assert "secret" not in repr(features)
    assert accumulator.window() == {}


def test_pointer_speed_requires_enough_samples_and_reset_clears_positions():
    accumulator = Accumulator()
    accumulator.move(0, 0, 0)
    assert accumulator.window() == {}
    for i in range(1, 12):
        accumulator.move(i * 10, 0, i * 0.1)
    assert abs(accumulator.window()["pointer_speed"] - 100) < 0.001
    accumulator.reset()
    assert accumulator.window() == {}
