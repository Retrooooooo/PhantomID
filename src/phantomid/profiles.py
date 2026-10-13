import json

from cryptography.fernet import Fernet

from .detector import validate_profile


class ProfileRepository:
    def __init__(self, store, keys=None):
        self.store = store
        if keys is None:
            import keyring

            backend = keyring.get_keyring()
            approved = {
                "keyring.backends.Windows.WinVaultKeyring",
                "keyring.backends.macOS.Keyring",
                "keyring.backends.SecretService.Keyring",
            }
            backend_name = f"{type(backend).__module__}.{type(backend).__name__}"
            if backend_name not in approved:
                raise RuntimeError(
                    "An approved OS-backed keyring is required; plaintext fallback is disabled."
                )
            keys = backend
        self.keys = keys

    def cipher(self):
        key = self.keys.get_password("PhantomID", "profile-encryption-v1")
        if key is None:
            if self.store.conn.execute("SELECT 1 FROM profiles LIMIT 1").fetchone():
                raise RuntimeError(
                    "Profile encryption key is missing; existing data was not changed."
                )
            key = Fernet.generate_key().decode("ascii")
            self.keys.set_password("PhantomID", "profile-encryption-v1", key)
        cipher = Fernet(key.encode("ascii"))
        existing = self.store.conn.execute(
            "SELECT payload FROM profiles LIMIT 1"
        ).fetchone()
        if existing:
            cipher.decrypt(existing["payload"])
        return cipher

    def require_consent(self, user_id):
        user = self.store.conn.execute(
            "SELECT consent FROM users WHERE id=?", (user_id,)
        ).fetchone()
        if not user or not user["consent"]:
            raise PermissionError("Active consent is required for behavioral profiles.")

    def save(self, user_id, profile):
        self.require_consent(user_id)
        validate_profile(profile)
        self.load(user_id)
        plaintext = json.dumps(
            {"user_id": user_id, "profile": profile}, allow_nan=False
        ).encode()
        encrypted = self.cipher().encrypt(plaintext)
        with self.store.conn:
            self.store.conn.execute(
                "INSERT INTO profiles(user_id, payload) VALUES (?, ?) ON CONFLICT(user_id) DO UPDATE SET payload=excluded.payload",
                (user_id, encrypted),
            )

    def load(self, user_id):
        row = self.store.conn.execute(
            "SELECT payload FROM profiles WHERE user_id=?", (user_id,)
        ).fetchone()
        if row is None:
            return None
        self.require_consent(user_id)
        payload = json.loads(self.cipher().decrypt(row["payload"]))
        if payload["user_id"] != user_id:
            raise ValueError("Encrypted profile belongs to a different account.")
        validate_profile(payload["profile"])
        return payload["profile"]

    def delete(self, user_id):
        with self.store.conn:
            self.store.conn.execute("DELETE FROM profiles WHERE user_id=?", (user_id,))
