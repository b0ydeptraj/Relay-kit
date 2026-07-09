import sqlite3
import time
from pathlib import Path

from relay_kit_v3.db_utils import get_wal_connection

class LaneLockManager:
    """
    V5.4.1 Lane Lock Manager.
    File-level mutex using SQLite WAL for safe concurrency across agents.
    """
    
    DEFAULT_DB_PATH = ".relay-kit/runtime/lane-locks.db"
    
    def __init__(self, project_path: str | Path):
        self.project_path = Path(project_path)
        self.db_path = self.project_path / self.DEFAULT_DB_PATH
        self.conn = get_wal_connection(self.db_path)
        self._init_db()
        
    def _init_db(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS lane_locks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                lane_id TEXT NOT NULL,
                file_path TEXT NOT NULL UNIQUE,
                agent_id TEXT,
                acquired_at REAL NOT NULL,
                ttl REAL NOT NULL
            )
        """)
        
    def acquire(self, lane_id: str, file_path: str, agent_id: str = "default", ttl_seconds: float = 300.0) -> bool:
        """
        Attempt to acquire a lock for a file.
        Returns True if successful, False if already locked by someone else.
        """
        self.clean_expired()
        
        try:
            now = time.time()
            # If the row exists but has the SAME lane_id, we can just update the TTL/acquired_at
            # Otherwise we'll try to insert and it will fail on UNIQUE constraint if already locked
            
            # Check if we already own it
            cursor = self.conn.execute("SELECT lane_id FROM lane_locks WHERE file_path = ?", (file_path,))
            row = cursor.fetchone()
            
            if row:
                if row["lane_id"] == lane_id:
                    # We own it, renew the lock
                    self.conn.execute(
                        "UPDATE lane_locks SET acquired_at = ?, ttl = ? WHERE file_path = ?",
                        (now, ttl_seconds, file_path)
                    )
                    return True
                else:
                    # Someone else owns it
                    return False
                    
            # Try to insert
            self.conn.execute(
                "INSERT INTO lane_locks (lane_id, file_path, agent_id, acquired_at, ttl) VALUES (?, ?, ?, ?, ?)",
                (lane_id, file_path, agent_id, now, ttl_seconds)
            )
            return True
            
        except sqlite3.IntegrityError:
            # Race condition: someone else inserted first
            return False

    def release(self, lane_id: str, file_path: str) -> bool:
        """
        Release a lock. Returns True if released, False if we didn't own it.
        """
        cursor = self.conn.execute("SELECT lane_id FROM lane_locks WHERE file_path = ?", (file_path,))
        row = cursor.fetchone()
        
        if row and row["lane_id"] == lane_id:
            self.conn.execute("DELETE FROM lane_locks WHERE file_path = ?", (file_path,))
            return True
            
        return False
        
    def release_all(self, lane_id: str):
        """Release all locks held by a specific lane."""
        self.conn.execute("DELETE FROM lane_locks WHERE lane_id = ?", (lane_id,))

    def clean_expired(self):
        """Remove locks that have exceeded their TTL."""
        now = time.time()
        self.conn.execute(
            "DELETE FROM lane_locks WHERE acquired_at + ttl < ?", 
            (now,)
        )

    def check_lock(self, file_path: str) -> dict | None:
        """Return lock info if a file is locked, else None."""
        self.clean_expired()
        cursor = self.conn.execute("SELECT lane_id, agent_id, acquired_at, ttl FROM lane_locks WHERE file_path = ?", (file_path,))
        row = cursor.fetchone()
        return dict(row) if row else None
        
    def close(self):
        """Close the database connection."""
        self.conn.close()
