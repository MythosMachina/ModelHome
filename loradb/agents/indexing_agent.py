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
        # Check existing table schema; recreate if outdated
        cur.execute("PRAGMA table_info(lora_index)")
        cols = [r[1] for r in cur.fetchall()]
        required = ["filename", "name", "architecture", "tags", "base_model"]
        if cols and cols != required:
            # Existing table uses an old schema, drop it so we can recreate
            cur.execute("DROP TABLE IF EXISTS lora_index")
        cur.execute(
            """
            CREATE VIRTUAL TABLE IF NOT EXISTS lora_index USING fts5(
                filename,
                name,
                architecture,
                tags,
                base_model
            )
            """
        )
        self.conn.commit()

    def add_metadata(self, data: Dict[str, str]) -> None:
        self.conn.execute(
            """
            INSERT INTO lora_index(filename, name, architecture, tags, base_model)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                data.get("filename", ""),
                data.get("modelspec.title", ""),
                data.get("modelspec.architecture", ""),
                data.get("ss_tag_frequency", ""),
                data.get("ss_base_model_version", ""),
            ),
        )
        self.conn.commit()

    def search(self, query: str) -> List[Dict[str, str]]:
        cur = self.conn.cursor()
        if query == "*":
            rows = cur.execute(
                "SELECT filename, name, architecture, tags, base_model FROM lora_index"
            ).fetchall()
        else:
            rows = cur.execute(
                "SELECT filename, name, architecture, tags, base_model FROM lora_index WHERE lora_index MATCH ?",
                (query,),
            ).fetchall()
        return [
            {
                "filename": r[0],
                "name": r[1],
                "architecture": r[2],
                "tags": r[3],
                "base_model": r[4],
            }
            for r in rows
        ]
