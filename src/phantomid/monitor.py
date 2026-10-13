from .capture import Capture
from .detector import Enrollment, score
from .profiles import ProfileRepository
from .session import AnomalyCounter


class Monitor:
    def __init__(self, store, capture=None, profiles=None):
        self.store = store
        self.capture = capture or Capture()
        self.profiles = profiles
        self.counter = AnomalyCounter()
        self.enrollment = Enrollment()
        self.profile = None
        self.user_id = None
        self.active = False
        self.evidence = 0
        self.status = "Monitoring off"

    def start(self, user_id):
        self.stop()
        user = self.store.conn.execute(
            "SELECT consent FROM users WHERE id=?", (user_id,)
        ).fetchone()
        if not user or not user["consent"]:
            raise PermissionError("Consent is required before monitoring.")
        self.profiles = self.profiles or ProfileRepository(self.store)
        self.profile = self.profiles.load(user_id)
        # Verify secure key storage before collecting enrollment data.
        self.profiles.cipher()
        self.user_id = user_id
        self.enrollment = Enrollment()
        self.capture.start(True)
        self.active = True
        self.status = (
            "Monitoring active" if self.profile else "Learning — detection not ready"
        )

    def stop(self):
        self.capture.stop()
        self.active = False
        self.counter.reset()
        self.status = "Monitoring paused"

    def clear(self):
        self.stop()
        self.enrollment = Enrollment()
        self.profile = None
        self.user_id = None

    def tick(self):
        if not self.active:
            return False
        user = self.store.conn.execute(
            "SELECT consent FROM users WHERE id=?", (self.user_id,)
        ).fetchone()
        if not user or not user["consent"]:
            self.clear()
            return False
        self.evidence += 1
        features = self.capture.window()
        if self.profile is None:
            self.enrollment.add(self.evidence, features)
            if self.enrollment.ready:
                profile = self.enrollment.profile()
                self.profiles.save(self.user_id, profile)
                self.profile = profile
                self.status = "Monitoring active"
            return False
        abnormal, _ = score(self.profile, features)
        if self.counter.evaluate(self.evidence, abnormal):
            self.stop()
            self.status = "Identity verification required"
            return True
        return False

    def progress(self):
        if self.profile:
            return "Profile ready • keyboard/pointer features available"
        counts = {name: len(values) for name, values in self.enrollment.samples.items()}
        return f"Keyboard {max(counts['key_dwell'], counts['key_interval'])}/30 • Pointer {counts['pointer_speed']}/30 qualifying windows"
