import math
import statistics

# Units: seconds for timing, pixels/second for speed, radians for turning.
FEATURES = {
    "key_dwell": ("keyboard", 0.02),
    "key_interval": ("keyboard", 0.03),
    "pointer_speed": ("pointer", 30.0),
    "pointer_turn": ("pointer", 0.2),
    "scroll_interval": ("scroll", 0.1),
    "scroll_burst": ("scroll", 0.1),
    "transition_interval": ("interaction", 0.5),
}
MIN_WINDOWS = 3  # Fast demo: 3 windows per stream (~5 sec active)  # Demo setting: faster college demo result


def validate_features(features):
    if not isinstance(features, dict) or set(features) - FEATURES.keys():
        raise ValueError("Only approved aggregate features are accepted.")
    for value in features.values():
        if (
            isinstance(value, bool)
            or not isinstance(value, (int, float))
            or not math.isfinite(value)
            or value < 0
        ):
            raise ValueError("Features must be finite nonnegative numbers.")


def validate_profile(profile):
    if (
        not isinstance(profile, dict)
        or set(profile) != {"version", "features"}
        or profile["version"] != 1
    ):
        raise ValueError("Unsupported profile schema.")
    features = profile["features"]
    if (
        not isinstance(features, dict)
        or not features
        or set(features) - FEATURES.keys()
    ):
        raise ValueError("Unsupported profile features.")
    for name, pair in features.items():
        if not isinstance(pair, (list, tuple)) or len(pair) != 2:
            raise ValueError("Invalid profile statistics.")
        validate_features({name: pair[0]})
        validate_features({name: pair[1]})
        if pair[1] < FEATURES[name][1]:
            raise ValueError("Profile scale below feature floor.")


class Enrollment:
    def __init__(self):
        self.samples = {name: [] for name in FEATURES}
        self.last_evidence = -1

    def add(self, evidence_id, features):
        validate_features(features)
        if evidence_id <= self.last_evidence:
            return
        self.last_evidence = evidence_id
        for name, value in features.items():
            if len(self.samples[name]) < MIN_WINDOWS:
                self.samples[name].append(value)

    @property
    def ready(self):
        return (
            len(
                {
                    FEATURES[name][0]
                    for name, values in self.samples.items()
                    if len(values) >= MIN_WINDOWS
                }
            )
            >= 2
        )

    def profile(self):
        if not self.ready:
            raise ValueError("Insufficient evidence: enroll at least two streams.")
        features = {}
        for name, values in self.samples.items():
            if len(values) >= MIN_WINDOWS:
                median = statistics.median(values)
                spread = 1.4826 * statistics.median(
                    abs(value - median) for value in values
                )
                features[name] = [median, max(spread, FEATURES[name][1])]
        return {"version": 1, "features": features}


def score(profile, features):
    validate_profile(profile)
    validate_features(features)
    streams = {}
    for name, value in features.items():
        if name not in profile["features"]:
            continue
        median, scale = profile["features"][name]
        streams.setdefault(FEATURES[name][0], []).append(abs(value - median) / scale)
    if not streams:
        return None, []
    stream_scores = {name: statistics.mean(values) for name, values in streams.items()}
    # shortcut: threshold is provisional; calibrate with held-out volunteer data before protection claims.
    return statistics.mean(stream_scores.values()) >= 3.0, [
        name for name, value in stream_scores.items() if value >= 3.0
    ]
