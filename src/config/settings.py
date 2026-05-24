from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
import os

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parents[2]
load_dotenv(BASE_DIR / ".env")


@dataclass(frozen=True)
class MongoSettings:
    uri: str | None
    database_name: str
    users_collection: str
    conversations_collection: str
    saved_queries_collection: str


@lru_cache(maxsize=1)
def get_mongo_settings() -> MongoSettings:
    return MongoSettings(
        uri=os.getenv("MONGO_URI") or None,
        database_name=os.getenv("MONGO_DB_NAME", "ask_my_data"),
        users_collection=os.getenv("MONGO_USERS_COLLECTION", "users"),
        conversations_collection=os.getenv(
            "MONGO_CONVERSATIONS_COLLECTION", "conversation_history"
        ),
        saved_queries_collection=os.getenv(
            "MONGO_SAVED_QUERIES_COLLECTION", "saved_queries"
        ),
    )
