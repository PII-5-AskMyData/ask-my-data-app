from datetime import datetime, timezone

from bson import ObjectId
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

    def save_interaction(self, payload: dict) -> bool:
        if not self.available:
            return False

        try:
            document = {
                **payload,
                "created_at": payload.get("created_at")
                or datetime.now(timezone.utc),
            }
            self.database[self.settings.conversations_collection].insert_one(document)
            return True
        except PyMongoError as error:
            print(f"Erro ao salvar interacao no MongoDB: {error}")
            return False

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
                item["id"] = str(item.pop("_id"))
                results.append(item)
            return results
        except PyMongoError:
            return []

    def update_interaction_charts(
        self,
        username: str | None,
        charts: list[dict],
        mongo_id: str | None = None,
        history_id: str | None = None,
        visualizacoes: list[dict] | None = None,
    ) -> bool:
        if not self.available:
            return False

        try:
            query: dict = {}
            if username:
                query["username"] = username
            if mongo_id:
                query["_id"] = ObjectId(mongo_id)
            elif history_id:
                query["history_id"] = history_id
            else:
                return False

            update_fields: dict = {"charts": charts}
            if visualizacoes:
                update_fields["visualizacoes"] = visualizacoes

            result = self.database[self.settings.conversations_collection].update_one(
                query,
                {"$set": update_fields},
            )
            return result.modified_count > 0 or result.matched_count > 0
        except (PyMongoError, ValueError) as error:
            print(f"Erro ao atualizar graficos no MongoDB: {error}")
            return False

    def delete_interaction(
        self,
        username: str | None,
        mongo_id: str | None = None,
        history_id: str | None = None,
    ) -> None:
        if not self.available:
            return

        try:
            query: dict = {}
            if username:
                query["username"] = username
            if mongo_id:
                query["_id"] = ObjectId(mongo_id)
            elif history_id:
                query["history_id"] = history_id
            else:
                return

            self.database[self.settings.conversations_collection].delete_one(query)
        except (PyMongoError, ValueError):
            return
