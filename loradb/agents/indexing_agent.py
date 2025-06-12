from typing import Dict, List

import sqlite3
from pathlib import Path

class IndexingAgent:
    """Maintain search index for LoRA metadata using SQLite FTS5."""

    def __init__(self, db_path: Path | None = None) -> None:
        self.db_path = Path(db_path or "loradb/search_index/index.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        self._ensure_table()

    def _ensure_table(self) -> None:
        cur = self.conn.cursor()
        cur.execute(
            "CREATE VIRTUAL TABLE IF NOT EXISTS lora_index USING fts5(filename, name, tags)"
        )
        self.conn.commit()

    def add_metadata(self, data: Dict[str, str]) -> None:
        self.conn.execute(
            "INSERT INTO lora_index(filename, name, tags) VALUES (?, ?, ?)",
            (
                data.get("filename", ""),
                data.get("name", ""),
                data.get("tags", ""),
            ),
        )
        self.conn.commit()

    def search(self, query: str) -> List[Dict[str, str]]:
        cur = self.conn.cursor()
        if query == "*":
            rows = cur.execute(
                "SELECT filename, name, tags FROM lora_index"
            ).fetchall()
        else:
            rows = cur.execute(
                "SELECT filename, name, tags FROM lora_index WHERE lora_index MATCH ?",
                (query,),
            ).fetchall()
        return [{"filename": r[0], "name": r[1], "tags": r[2]} for r in rows]
