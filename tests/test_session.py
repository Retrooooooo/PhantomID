from phantomid.session import AnomalyCounter


def test_third_fresh_anomaly_challenges_immediately():
    counter = AnomalyCounter()
    assert not counter.evaluate(1, True)
    assert not counter.evaluate(1, True)
    assert not counter.evaluate(2, True)
    assert counter.evaluate(3, True)
    assert counter.challenged


def test_normal_or_insufficient_evidence_breaks_streak():
    for result in (False, None):
        counter = AnomalyCounter()
        counter.evaluate(1, True)
        counter.evaluate(2, result)
        assert counter.consecutive == 0
        assert not counter.evaluate(3, True)
        counter.reset()
        assert not counter.challenged
        assert counter.consecutive == 0
