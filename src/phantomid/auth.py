import re
import time

from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError


class Auth:
    def __init__(self, store, clock=time.monotonic):
        self.store = store
        self.clock = clock
        self.hasher = PasswordHasher()
        self.failures = {}
        self.dummy_hash = self.hasher.hash("not-an-account-password")

    def register(self, username, password, actor_id=None):
        username = username.strip()
        if not re.fullmatch(r"[A-Za-z0-9_.-]{3,32}", username):
            raise ValueError("Use 3–32 letters, numbers, dots, underscores or hyphens.")
        if not 12 <= len(password) <= 1024:
            raise ValueError("Use a password between 12 and 1024 characters.")
        users = self.store.users()
        if users and not any(
            user["id"] == actor_id and user["role"] == "admin" for user in users
        ):
            raise PermissionError("Administrator authorization required.")
        self.store.add_user(
            username, "user" if users else "admin", self.hasher.hash(password)
        )
        return self.store.find_user(username)

    def login(self, username, password):
        key = username.strip().casefold()
        count, until = self.failures.get(key, (0, 0))
        if self.clock() < until:
            raise ValueError("Wait a moment before trying again.")
        user = self.store.find_user(username.strip())
        encoded = (
            user["password_hash"] if user and user["password_hash"] else self.dummy_hash
        )
        try:
            valid = self.hasher.verify(encoded, password)
        except (VerificationError, InvalidHashError):
            valid = False
        if not valid or not user or not user["password_hash"]:
            count += 1
            self.failures[key] = (count, self.clock() + min(2 ** min(count, 6), 30))
            raise ValueError("Incorrect username or password.")
        self.failures.pop(key, None)
        return user
