import os
import json
import datetime as _dt
from typing import Any, Dict, Optional

try:
    from pymongo import MongoClient  # type: ignore
except Exception:  # pragma: no cover
    MongoClient = None  # type: ignore


def _now_iso() -> str:
    return _dt.datetime.utcnow().isoformat() + "Z"


class SessionStore:
    """Persist session history to MongoDB if available, else to a local JSONL file."""

    def __init__(self, db_name: str = "jarvis", collection: str = "sessions"):
        self.mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
        self.db_name = db_name
        self.collection = collection
        self._client = None
        self._col = None
        self._file_path = os.path.join(os.getcwd(), "sessions.jsonl")
        self._connect()

    def _connect(self):
        if MongoClient is None:
            return
        try:
            self._client = MongoClient(self.mongo_uri, serverSelectionTimeoutMS=1000)
            # quick ping
            self._client.admin.command('ping')
            self._col = self._client[self.db_name][self.collection]
        except Exception:
            self._client = None
            self._col = None

    def start_session(self, meta: Optional[Dict[str, Any]] = None) -> str:
        sid = os.urandom(8).hex()
        doc = {
            "_id": sid,
            "createdAt": _now_iso(),
            "meta": meta or {},
            "events": [],
        }
        if self._col is not None:
            try:
                self._col.insert_one(doc)
                return sid
            except Exception:
                pass
        # file fallback: append a create event
        self._append_file({"type": "session_start", "sessionId": sid, "doc": doc})
        return sid

    def append_event(self, session_id: str, event: Dict[str, Any]):
        event = {**event, "ts": _now_iso(), "sessionId": session_id}
        if self._col is not None:
            try:
                self._col.update_one({"_id": session_id}, {"$push": {"events": event}}, upsert=True)
                return
            except Exception:
                pass
        self._append_file({"type": "event", **event})

    def end_session(self, session_id: str, meta: Optional[Dict[str, Any]] = None):
        update = {"endedAt": _now_iso(), "endMeta": meta or {}}
        if self._col is not None:
            try:
                self._col.update_one({"_id": session_id}, {"$set": update}, upsert=True)
                return
            except Exception:
                pass
        self._append_file({"type": "session_end", "sessionId": session_id, **update})

    def _append_file(self, obj: Dict[str, Any]):
        try:
            with open(self._file_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(obj, ensure_ascii=False) + "\n")
        except Exception:
            pass
