from __future__ import annotations

import logging
from typing import Any

from pymongo import MongoClient
from pymongo.collection import Collection

log = logging.getLogger(__name__)


class OsEventTimeline:
    def __init__(self, mongo_url: str | None) -> None:
        self._client: MongoClient | None = None
        self._col: Collection | None = None
        if mongo_url:
            self._client = MongoClient(mongo_url, serverSelectionTimeoutMS=2000)
            self._col = self._client.get_database("oficina_os").get_collection("os_events")

    def append(self, os_id: int, routing_key: str, payload: dict[str, Any]) -> None:
        if self._col is None:
            return
        try:
            self._col.insert_one(
                {"os_id": os_id, "routing_key": routing_key, "payload": payload}
            )
        except Exception:  # noqa: BLE001
            log.warning("falha ao gravar timeline mongo os_id=%s", os_id)

    def list_by_os(self, os_id: int, limit: int = 50) -> list[dict[str, Any]]:
        if self._col is None:
            return []
        return list(self._col.find({"os_id": os_id}, {"_id": 0}).sort("_id", -1).limit(limit))

    def ping(self) -> bool:
        if self._client is None:
            return True
        try:
            self._client.admin.command("ping")
            return True
        except Exception:  # noqa: BLE001
            return False
