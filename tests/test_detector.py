import pytest

from phantomid.detector import Enrollment, score
from phantomid.session import AnomalyCounter


def test_sample_readiness_has_no_duration_gate_and_normal_scores_low():
    enrollment = Enrollment()
    for evidence in range(30):
        enrollment.add(
            evidence,
            {
                "key_dwell": 0.10 + evidence % 2 * 0.01,
                "pointer_speed": 100 + evidence % 2 * 10,
            },
        )
    assert enrollment.ready
    profile = enrollment.profile()
    assert score(profile, {"key_dwell": 0.105, "pointer_speed": 105})[0] is False
    counter = AnomalyCounter()
    for evidence in range(3):
        abnormal, streams = score(profile, {"key_dwell": 0.8, "pointer_speed": 900})
        assert abnormal and set(streams) == {"keyboard", "pointer"}
        assert counter.evaluate(evidence, abnormal) is (evidence == 2)


def test_duplicates_sparse_streams_and_unknown_features_do_not_enroll():
    enrollment = Enrollment()
    for _ in range(30):
        enrollment.add(1, {"key_dwell": 0.1, "pointer_speed": 100})
    assert not enrollment.ready
    with pytest.raises(ValueError, match="Insufficient"):
        enrollment.profile()
    with pytest.raises(ValueError):
        enrollment.add(2, {"typed_text": "password"})


def test_missing_and_nonfinite_evidence_is_not_normal_or_abnormal():
    enrollment = Enrollment()
    for evidence in range(30):
        enrollment.add(evidence, {"key_dwell": 0.1, "pointer_speed": 100})
    profile = enrollment.profile()
    assert score(profile, {}) == (None, [])
    with pytest.raises(ValueError):
        score(profile, {"key_dwell": float("nan")})
