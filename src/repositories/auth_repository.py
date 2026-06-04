from __future__ import annotations

import hashlib
import hmac

from pymongo.errors import PyMongoError

from src.config.settings import get_mongo_settings
from src.db.mongo import get_mongo_database, is_mongo_enabled


def _hash_password(password: str, salt: str) -> str:
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        120_000,
    )
    return digest.hex()


class AuthRepository:
    def __init__(self) -> None:
        self.database = get_mongo_database()
        self.settings = get_mongo_settings()

    @property
    def available(self) -> bool:
        return is_mongo_enabled() and self.database is not None

    def authenticate(self, username: str, password: str) -> dict | None:
        if not self.available:
            return None

        try:
            user = self.database[self.settings.users_collection].find_one(
                {"username": username}
            )
            if not user or not user.get("is_active", True):
                return None

            if user.get("password_hash") and user.get("password_salt"):
                expected = _hash_password(password, user["password_salt"])
                if not hmac.compare_digest(expected, user["password_hash"]):
                    return None
            elif user.get("password") != password:
                return None

            return {
                "username": user.get("username"),
                "display_name": user.get("display_name") or user.get("username"),
                "roles": user.get("roles", []),
            }
        except PyMongoError:
            return None
