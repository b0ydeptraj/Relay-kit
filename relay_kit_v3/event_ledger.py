import sqlite3
import json
import datetime
from pathlib import Path

from relay_kit_v3.db_utils import get_wal_connection

class EventLedger:
    """
    V5.4.2 Event Ledger.
    Append-only event log using SQLite WAL.
    """
    
    DEFAULT_DB_PATH = ".relay-kit/runtime/event-ledger.db"
    
    def __init__(self, project_path: str | Path):
        self.project_path = Path(project_path)
        self.db_path = self.project_path / self.DEFAULT_DB_PATH
        self.conn = get_wal_connection(self.db_path)
        self._init_db()
        
    def _init_db(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                event_type TEXT NOT NULL,
                lane_id TEXT NOT NULL,
                details TEXT NOT NULL
            )
        """)
        
    def log_event(self, event_type: str, lane_id: str, details: dict) -> int:
        """
        Log an event to the ledger.
        Returns the event ID.
        """
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        details_json = json.dumps(details, ensure_ascii=False)
        
        cursor = self.conn.execute(
            "INSERT INTO events (timestamp, event_type, lane_id, details) VALUES (?, ?, ?, ?)",
            (timestamp, event_type, lane_id, details_json)
        )
        return cursor.lastrowid

    def read_events(self, lane_id: str = None, limit: int = 100) -> list[dict]:
        """
        Read the latest events.
        """
        if lane_id:
            cursor = self.conn.execute(
                "SELECT * FROM events WHERE lane_id = ? ORDER BY id DESC LIMIT ?",
                (lane_id, limit)
            )
        else:
            cursor = self.conn.execute(
                "SELECT * FROM events ORDER BY id DESC LIMIT ?",
                (limit,)
            )
            
        events = []
        for row in cursor.fetchall():
            event = dict(row)
            event["details"] = json.loads(event["details"])
            events.append(event)
            
        return events

    def close(self):
        """Close the database connection."""
        self.conn.close()
