# Calibration Notes (Not Completed — Documented Only)

What needs real-device measurement:
- Key dwell / interval distributions across users, keyboards, fatigue states.
- Pointer speed / direction-change distributions at normal and altered settings.
- Scroll burst patterns with different devices (wheel vs trackpad vs touch).
- Transition timing between apps/windows (content-free only).

What must not be invented:
- No fixed accuracy percentage.
- No universal threshold until held-out data supports it.
- No claim that behavioral patterns prove identity.

Current status: synthetic fixtures verify logic (test_detector.py, test_capture.py).
Real calibration requires consenting participants, multiple days, multiple devices,
and comparison against same-user / different-user / changed-device cases.

Shortcut comment (per ponytail): calibration and evaluation use synthetic fixtures; real-device verification is deferred until voluntary participant review.
