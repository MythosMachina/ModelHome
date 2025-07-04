import sqlite3
from pathlib import Path
from typing import Dict, List, Optional

from passlib.hash import bcrypt

import config


class AuthManager:
    """Manage user accounts stored in the main SQLite database."""

    def __init__(self, db_path: Path | None = None) -> None:
        self.db_path = Path(db_path or "loradb/search_index/index.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self._ensure_table()

    def _ensure_table(self) -> None:
        self.conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password_hash TEXT,
                role TEXT
            )
            """
        )
        self.conn.commit()

    def create_user(self, username: str, password: str, role: str = "user") -> None:
        """Create or replace ``username`` with ``password`` and ``role``."""
        pw_hash = bcrypt.hash(password)
        self.conn.execute(
            "INSERT OR REPLACE INTO users(username, password_hash, role) VALUES (?, ?, ?)",
            (username, pw_hash, role),
        )
        self.conn.commit()

    def verify_user(self, username: str, password: str) -> bool:
        cur = self.conn.cursor()
        row = cur.execute(
            "SELECT password_hash FROM users WHERE username = ?",
            (username,),
        ).fetchone()
        if not row:
            return False
        return bcrypt.verify(password, row[0])

    def get_user(self, username: str) -> Optional[Dict]:
        row = self.conn.execute(
            "SELECT id, username, role FROM users WHERE username = ?",
            (username,),
        ).fetchone()
        if row:
            return {"id": row[0], "username": row[1], "role": row[2]}
        return None

    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        row = self.conn.execute(
            "SELECT id, username, role FROM users WHERE id = ?",
            (user_id,),
        ).fetchone()
        if row:
            return {"id": row[0], "username": row[1], "role": row[2]}
        return None

    def list_users(self) -> List[Dict]:
        rows = self.conn.execute(
            "SELECT id, username, role FROM users ORDER BY username"
        ).fetchall()
        return [{"id": r[0], "username": r[1], "role": r[2]} for r in rows]

    def delete_user(self, username: str) -> None:
        self.conn.execute("DELETE FROM users WHERE username = ?", (username,))
        self.conn.commit()
