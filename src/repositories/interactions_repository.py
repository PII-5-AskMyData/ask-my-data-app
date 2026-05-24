from datetime import datetime, timezone

from pymongo.errors import PyMongoError

from src.config.settings import get_mongo_settings
from src.db.mongo import get_mongo_database, is_mongo_enabled


class InteractionsRepository:
    def __init__(self) -> None:
        self.database = get_mongo_database()
        self.settings = get_mongo_settings()

    @property
    def available(self) -> bool:
        return is_mongo_enabled() and self.database is not None

    def save_interaction(self, payload: dict) -> None:
        if not self.available:
            return

        try:
            document = {
                **payload,
                "created_at": datetime.now(timezone.utc),
            }
            self.database[self.settings.conversations_collection].insert_one(document)
        except PyMongoError:
            return

    def list_interactions(
        self, username: str | None = None, limit: int = 25
    ) -> list[dict]:
        if not self.available:
            return []

        try:
            query = {}
            if username:
                query["username"] = username

            cursor = (
                self.database[self.settings.conversations_collection]
                .find(query)
                .sort("created_at", -1)
                .limit(limit)
            )

            results = []
            for item in cursor:
                item.pop("_id", None)
                results.append(item)
            return results
        except PyMongoError:
            return []
