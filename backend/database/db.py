"""
SQLite database — stores scan history.
"""
import sqlite3
import json
import os
from datetime import datetime
from contextlib import closing

import tempfile

def _get_db_path():
    if os.environ.get("VERCEL") or os.environ.get("AWS_EXECUTION_ENV"):
        return "/tmp/history.db"
    try:
        local_path = os.path.join(os.path.dirname(__file__), "..", "history.db")
        # Try to open/create the file to check write permissions
        with open(local_path, "a"):
            pass
        return local_path
    except Exception:
        return os.path.join(tempfile.gettempdir(), "history.db")

DB_PATH = _get_db_path()

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
            conn.execute("""
                CREATE TABLE IF NOT EXISTS api_keys (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key_hash TEXT UNIQUE NOT NULL,
                    user_id TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    is_active INTEGER DEFAULT 1
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS transfers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    code TEXT UNIQUE NOT NULL,
                    file_name TEXT NOT NULL,
                    file_path TEXT NOT NULL,
                    expires_at TEXT NOT NULL
                )
            """)

import hashlib
import secrets

def generate_api_key(user_id: str = "default_user"):
    """Generate a new API key and store its hash."""
    raw_key = "fd_" + secrets.token_urlsafe(32)
    key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
    
    with closing(get_connection()) as conn:
        with conn:
            conn.execute(
                "INSERT INTO api_keys (key_hash, user_id, created_at) VALUES (?, ?, ?)",
                (key_hash, user_id, datetime.utcnow().isoformat())
            )
    return raw_key

def validate_api_key(raw_key: str) -> bool:
    """Check if an API key is valid and active."""
    key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
    with closing(get_connection()) as conn:
        row = conn.execute(
            "SELECT id FROM api_keys WHERE key_hash = ? AND is_active = 1",
            (key_hash,)
        ).fetchone()
        return bool(row)


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

import random
from datetime import timedelta

def create_transfer(file_name: str, file_path: str, minutes: int = 10) -> str:
    """Create a new file transfer with a 6-digit code."""
    expires = (datetime.utcnow() + timedelta(minutes=minutes)).isoformat()
    with closing(get_connection()) as conn:
        with conn:
            # Generate unique 6 digit code
            while True:
                code = str(random.randint(100000, 999999))
                if not conn.execute("SELECT id FROM transfers WHERE code = ?", (code,)).fetchone():
                    break
                    
            conn.execute(
                "INSERT INTO transfers (code, file_name, file_path, expires_at) VALUES (?, ?, ?, ?)",
                (code, file_name, file_path, expires)
            )
            return code

def get_transfer(code: str):
    """Retrieve transfer if not expired."""
    with closing(get_connection()) as conn:
        row = conn.execute("SELECT * FROM transfers WHERE code = ?", (code,)).fetchone()
        if not row:
            return None
            
        data = dict(row)
        if datetime.utcnow().isoformat() > data['expires_at']:
            # Expired
            delete_transfer(code)
            return None
            
        return dict(row)

def delete_transfer(code: str):
    """Delete transfer record from db."""
    with closing(get_connection()) as conn:
        with conn:
            conn.execute("DELETE FROM transfers WHERE code = ?", (code,))

def cleanup_expired_transfers_db():
    """Find expired transfers, delete them from DB and return file paths to delete."""
    now = datetime.utcnow().isoformat()
    paths_to_delete = []
    with closing(get_connection()) as conn:
        rows = conn.execute("SELECT code, file_path FROM transfers WHERE expires_at < ?", (now,)).fetchall()
        with conn:
            for row in rows:
                paths_to_delete.append(row["file_path"])
                conn.execute("DELETE FROM transfers WHERE code = ?", (row["code"],))
    return paths_to_delete
