import sqlite3
from pathlib import Path

def get_wal_connection(db_path: Path) -> sqlite3.Connection:
    """
    Get an SQLite connection with WAL (Write-Ahead Logging) enabled.
    This provides better concurrency and safety for multi-lane scenarios.
    """
    # Ensure directory exists
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    # timeout=30.0 helps with concurrent writes waiting for lock
    conn = sqlite3.connect(db_path, timeout=30.0, isolation_level=None)
    
    # Enable WAL mode
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    
    # Row factory to return dict-like objects
    conn.row_factory = sqlite3.Row
    return conn
