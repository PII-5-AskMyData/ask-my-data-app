from functools import lru_cache

from pymongo import MongoClient
from pymongo.database import Database

from src.config.settings import get_mongo_settings


@lru_cache(maxsize=1)
def get_mongo_client() -> MongoClient | None:
    settings = get_mongo_settings()
    if not settings.uri:
        return None
    return MongoClient(settings.uri, serverSelectionTimeoutMS=5000)


def get_mongo_database() -> Database | None:
    client = get_mongo_client()
    if client is None:
        return None
    return client[get_mongo_settings().database_name]


def is_mongo_enabled() -> bool:
    return get_mongo_client() is not None
