import pytest

from phantomid.auth import Auth
from phantomid.storage import Store


def test_first_account_is_admin_and_additions_require_admin(tmp_path):
    with Store(tmp_path / "accounts.db") as store:
        auth = Auth(store)
        alice = auth.register("alice", "long password 123")
        assert alice["role"] == "admin"
        with pytest.raises(PermissionError):
            auth.register("bob", "long password 456")
        bob = auth.register("bob", "long password 456", actor_id=alice["id"])
        assert bob["role"] == "user"
        with pytest.raises(PermissionError):
            auth.register("carol", "long password 789", actor_id=bob["id"])
        assert store.find_user("alice")["password_hash"] != "long password 123"


def test_login_throttles_and_accepts_correct_password_after_delay(tmp_path):
    now = [0.0]
    with Store(tmp_path / "accounts.db") as store:
        auth = Auth(store, clock=lambda: now[0])
        auth.register("alice", "long password 123")
        with pytest.raises(ValueError, match="Incorrect"):
            auth.login("alice", "wrong")
        with pytest.raises(ValueError, match="Wait"):
            auth.login("alice", "long password 123")
        now[0] = 2.0
        assert auth.login("ALICE", "long password 123")["username"] == "alice"


@pytest.mark.parametrize(
    "username,password",
    [("a", "long password 123"), ("alice", "short"), ("a/b", "long password 123")],
)
def test_registration_validates_inputs(tmp_path, username, password):
    with Store(tmp_path / "accounts.db") as store, pytest.raises(ValueError):
        Auth(store).register(username, password)
