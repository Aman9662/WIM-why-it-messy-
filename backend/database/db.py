"""
SQLite database — stores scan history.
"""
import sqlite3
import json
import os
from datetime import datetime
from contextlib import closing

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "history.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize database tables."""
    with closing(get_connection()) as conn:
        with conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS scans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    detection_type TEXT NOT NULL,
                    input_preview TEXT NOT NULL,
                    input_source TEXT NOT NULL,
                    score REAL NOT NULL,
                    verdict TEXT NOT NULL,
                    confidence TEXT NOT NULL,
                    full_result TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)


def save_scan(detection_type: str, input_preview: str, input_source: str, result: dict):
    """Save a scan result to history and return its ID."""
    with closing(get_connection()) as conn:
        with conn:
            cursor = conn.execute("""
                INSERT INTO scans
                (detection_type, input_preview, input_source, score, verdict, confidence, full_result, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                detection_type,
                input_preview[:200],
                input_source,
                result.get("score", 0),
                result.get("verdict", "Unknown"),
                result.get("confidence", "Low"),
                json.dumps(result),
                datetime.utcnow().isoformat()
            ))
            return cursor.lastrowid


def get_history(limit: int = 50):
    """Retrieve scan history."""
    with closing(get_connection()) as conn:
        rows = conn.execute(
            "SELECT * FROM scans ORDER BY created_at DESC LIMIT ?", (limit,)
        ).fetchall()
        return [dict(row) for row in rows]


def get_scan_by_id(scan_id: int):
    """Retrieve a single scan by ID."""
    with closing(get_connection()) as conn:
        row = conn.execute("SELECT * FROM scans WHERE id = ?", (scan_id,)).fetchone()
        if row:
            result = dict(row)
            result["full_result"] = json.loads(result["full_result"])
            return result
        return None


def delete_scan(scan_id: int):
    """Delete a scan from history."""
    with closing(get_connection()) as conn:
        with conn:
            conn.execute("DELETE FROM scans WHERE id = ?", (scan_id,))
