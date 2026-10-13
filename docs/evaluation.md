# PhantomID — Evaluation (Actual Results Only)

## What was verified
- 22 tests pass (pytest, no skipped assertions).
- Auth/account isolation: usernames case-insensitive, admin-first, no plaintext passwords.
- Consent gate: monitoring does not start; withdrawal stops capture; event history retains only type/timestamp.
- Profile encryption: Fernet ciphertext stored; no plaintext fallback; missing/invalid key does not overwrite existing ciphertext; wrong-account payload rejected.
- Detector/enrollment: 30 qualifying fresh windows across 2 streams; duplicates/sparse streams excluded; profile produces median + scale; score compares to baseline; 3 consecutive abnormal windows trigger challenge.
- Capture: keyboard/pointer/scroll events accumulate aggregate statistics only; key identity and pointer paths discarded after calculation; listener stops before password dialog; overflow invalidates data.
- Guest: session folder verified; approved-resource only; cleanup refuses symlink/reparse or missing ownership.
- Dashboard: all pages render; consent dialog requires explicit check; privacy info states collection limits; overlay displays verification request; demonstration only—not an OS lock.

## What was not verified
- Real-device calibration: thresholds (3.0) are provisional; no held-out volunteer data; false-positive rate unknown.
- OS-keyring integration on this machine (keyring backend selected but not tested under real user session).
- Window-title/content-only interaction-flow stream (not implemented; no window-title capture).
- Startup/uninstall automation fully verified (application launches with `python -m phantomid`; no registered service or uninstall script completed).
- Third-party audit of dependency vulnerabilities not performed (only installed audited packages available).
- No external network transmission verified (application is local-only by design).

## Honest limitations
- Behavioral biometrics are not proof of identity; a user who knows the password can pass verification.
- The overlay does not defeat Windows security controls; it is a demonstration window only.
- Guest controls apply inside PhantomID, not to the whole OS.
- Profiles are encrypted locally but a sufficiently privileged attacker or backup copy could access the data.
- Synthetic fixtures test logic; they do not represent real interaction patterns.
- The system requires consent and is designed to be disabled by withdrawal or admin.
