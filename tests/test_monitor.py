from test_profiles import MemoryKeyring

from phantomid.monitor import Monitor
from phantomid.profiles import ProfileRepository
from phantomid.storage import Store


class FakeCapture:
    def __init__(self):
        self.active = False
        self.features = {"key_dwell": 0.1, "pointer_speed": 100}

    def start(self, consent):
        assert consent
        self.active = True

    def stop(self):
        self.active = False

    def window(self):
        assert self.active
        return self.features


def test_enrollment_monitoring_and_third_anomaly_stop_capture(tmp_path):
    with Store(tmp_path / "monitor.db") as store:
        user = store.add_user("alice", "admin", "hash")
        store.set_consent(user, True)
        capture = FakeCapture()
        monitor = Monitor(store, capture, ProfileRepository(store, MemoryKeyring()))
        monitor.start(user)
        for _ in range(30):
            assert not monitor.tick()
        assert monitor.profile is not None
        capture.features = {"key_dwell": 1.0, "pointer_speed": 1000}
        assert not monitor.tick()
        assert not monitor.tick()
        assert monitor.tick()
        assert not capture.active
        monitor.start(user)
        assert monitor.counter.consecutive == 0
        store.set_consent(user, False)
        assert not monitor.tick()
        assert not capture.active
        assert monitor.profile is None
