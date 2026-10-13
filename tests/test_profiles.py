import pytest
from cryptography.fernet import Fernet, InvalidToken

from phantomid.profiles import ProfileRepository
from phantomid.storage import Store


class MemoryKeyring:
    def __init__(self):
        self.value = None

    def get_password(self, service, account):
        return self.value

    def set_password(self, service, account, value):
        self.value = value


def test_profiles_are_encrypted_bound_to_account_and_require_consent(tmp_path):
    with Store(tmp_path / "profiles.db") as store:
        alice = store.add_user("alice", "admin", "hash")
        bob = store.add_user("bob", "user", "hash")
        keys = MemoryKeyring()
        repo = ProfileRepository(store, keys)
        profile = {"version": 1, "features": {"key_dwell": [0.1, 0.02]}}
        with pytest.raises(PermissionError):
            repo.save(alice, profile)
        store.set_consent(alice, True)
        repo.save(alice, profile)
        assert repo.load(alice) == profile
        assert repo.load(bob) is None
        blob = store.conn.execute("SELECT payload FROM profiles").fetchone()[0]
        assert b"key_dwell" not in blob
        store.conn.execute(
            "INSERT INTO profiles(user_id, payload) VALUES (?, ?)", (bob, blob)
        )
        store.set_consent(bob, True)
        with pytest.raises(ValueError, match="account"):
            repo.load(bob)
        store.set_consent(alice, False)
        with pytest.raises(PermissionError):
            repo.load(alice)
        repo.delete(alice)
        assert repo.load(alice) is None


def test_missing_key_never_replaces_key_or_existing_ciphertext(tmp_path):
    with Store(tmp_path / "profiles.db") as store:
        user = store.add_user("alice", "admin", "hash")
        store.set_consent(user, True)
        keys = MemoryKeyring()
        repo = ProfileRepository(store, keys)
        repo.save(user, {"version": 1, "features": {"key_dwell": [0.1, 0.02]}})
        keys.value = None
        with pytest.raises(RuntimeError, match="missing"):
            repo.load(user)
        assert keys.value is None
        keys.value = Fernet.generate_key().decode()
        with pytest.raises(InvalidToken):
            repo.load(user)
        before = store.conn.execute("SELECT payload FROM profiles").fetchone()[0]
        with pytest.raises(InvalidToken):
            repo.save(user, {"version": 1, "features": {"key_dwell": [0.2, 0.02]}})
        assert (
            store.conn.execute("SELECT payload FROM profiles").fetchone()[0] == before
        )


def test_arbitrary_content_cannot_be_saved_as_profile(tmp_path):
    with Store(tmp_path / "profiles.db") as store:
        user = store.add_user("alice", "admin", "hash")
        store.set_consent(user, True)
        with pytest.raises(ValueError):
            ProfileRepository(store, MemoryKeyring()).save(
                user, {"typed_text": "secret"}
            )
