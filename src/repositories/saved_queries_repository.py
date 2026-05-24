from datetime import datetime, timezone

from bson import ObjectId
from pymongo.errors import PyMongoError

from src.config.settings import get_mongo_settings
from src.db.mongo import get_mongo_database, is_mongo_enabled


class SavedQueriesRepository:
    def __init__(self) -> None:
        self.database = get_mongo_database()
        self.settings = get_mongo_settings()

    @property
    def available(self) -> bool:
        return is_mongo_enabled() and self.database is not None

    def list_saved_queries(self, username: str | None = None) -> list[dict]:
        if not self.available:
            return []

        try:
            query = {}
            if username:
                query["username"] = username

            cursor = (
                self.database[self.settings.saved_queries_collection]
                .find(query)
                .sort("created_at", -1)
            )

            results = []
            for item in cursor:
                item["id"] = str(item.pop("_id"))
                results.append(item)
            return results
        except PyMongoError:
            return []

    def save_saved_query(
        self, username: str, title: str, description: str, sql: str
    ) -> None:
        if not self.available:
            return

        try:
            self.database[self.settings.saved_queries_collection].insert_one(
                {
                    "username": username,
                    "title": title,
                    "description": description,
                    "sql": sql,
                    "created_at": datetime.now(timezone.utc),
                    "updated_at": datetime.now(timezone.utc),
                }
            )
        except PyMongoError:
            return

    def update_saved_query(
        self,
        query_id: str,
        username: str,
        title: str,
        description: str,
        sql: str,
    ) -> None:
        if not self.available:
            return

        try:
            self.database[self.settings.saved_queries_collection].update_one(
                {"_id": ObjectId(query_id), "username": username},
                {
                    "$set": {
                        "title": title,
                        "description": description,
                        "sql": sql,
                        "updated_at": datetime.now(timezone.utc),
                    }
                },
            )
        except (PyMongoError, ValueError):
            return

    def delete_saved_query(self, query_id: str, username: str) -> None:
        if not self.available:
            return

        try:
            self.database[self.settings.saved_queries_collection].delete_one(
                {"_id": ObjectId(query_id), "username": username}
            )
        except (PyMongoError, ValueError):
            return
