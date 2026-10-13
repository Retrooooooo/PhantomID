import sqlite3

import pytest

from phantomid.storage import Store


def test_accounts_persist_and_usernames_are_case_insensitive(tmp_path):
    path = tmp_path / "accounts.db"
    with Store(path) as store:
        user_id = store.add_user("alice", "admin", "hashed-password")
        with pytest.raises(sqlite3.IntegrityError):
            store.add_user("ALICE", "user", "other-hash")
    with Store(path) as store:
        assert store.find_user("ALICE")["id"] == user_id
        assert store.find_user("alice")["role"] == "admin"


def test_consent_is_isolated_and_events_contain_only_metadata(tmp_path):
    with Store(tmp_path / "accounts.db") as store:
        alice = store.add_user("alice", "admin", "hash")
        bob = store.add_user("bob", "user", "hash")
        store.set_consent(alice, True)
        assert store.find_user("alice")["consent"] == 1
        assert store.find_user("bob")["consent"] == 0
        store.add_event(alice, "consent_accepted")
        assert len(store.events(alice)) == 1
        assert store.events(bob) == []
        with pytest.raises(ValueError):
            store.add_event(alice, "typed_password")
