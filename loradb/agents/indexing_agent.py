from typing import Dict, List

import sqlite3
from pathlib import Path

import config
from .metadata_extractor_agent import MetadataExtractorAgent

class IndexingAgent:
    """Maintain search index for LoRA metadata using SQLite FTS5."""

    def __init__(self, db_path: Path | None = None) -> None:
        self.db_path = Path(db_path or "loradb/search_index/index.db")
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(self.db_path)
        recreated = self._ensure_table()
        if recreated or self._is_index_empty():
            self.reindex_all()

    def _ensure_table(self) -> bool:
        cur = self.conn.cursor()
        # Check existing table schema; recreate if outdated
        cur.execute("PRAGMA table_info(lora_index)")
        cols = [r[1] for r in cur.fetchall()]
        required = ["filename", "name", "architecture", "tags", "base_model"]
        recreated = False
        if not cols:
            # Table did not exist, we'll need to index from scratch
            recreated = True
        elif cols != required:
            # Existing table uses an old schema, drop it so we can recreate
            cur.execute("DROP TABLE IF EXISTS lora_index")
            recreated = True
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
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS lora_category_map (
                filename TEXT,
                category_id INTEGER,
                UNIQUE(filename, category_id)
            )
            """
        )
        self.conn.commit()
        return recreated

    def _is_index_empty(self) -> bool:
        """Return True if the index table has no rows."""
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*) FROM lora_index")
        count = cur.fetchone()[0]
        return count == 0

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

    def reindex_all(self) -> None:
        """Index all safetensors files found in the upload directory."""
        uploads = Path(config.UPLOAD_DIR)
        if not uploads.exists():
            return
        extractor = MetadataExtractorAgent()
        for file in uploads.glob("*.safetensors"):
            meta = extractor.extract(file)
            self.add_metadata(meta)

    def remove_metadata(self, filename: str) -> None:
        """Remove a LoRA entry from the index by filename."""
        self.conn.execute(
            "DELETE FROM lora_index WHERE filename = ?",
            (filename,),
        )
        self.conn.commit()

    # --- Category management helpers ------------------------------------

    def create_category(self, name: str) -> int:
        """Create a category if it does not exist and return its id."""
        cur = self.conn.cursor()
        cur.execute("INSERT OR IGNORE INTO categories(name) VALUES (?)", (name,))
        self.conn.commit()
        cur.execute("SELECT id FROM categories WHERE name = ?", (name,))
        row = cur.fetchone()
        return int(row[0]) if row else 0

    def list_categories(self) -> List[Dict[str, str]]:
        cur = self.conn.cursor()
        rows = cur.execute("SELECT id, name FROM categories ORDER BY name").fetchall()
        return [{"id": r[0], "name": r[1]} for r in rows]

    def assign_category(self, filename: str, category_id: int) -> None:
        self.conn.execute(
            "INSERT OR IGNORE INTO lora_category_map(filename, category_id) VALUES (?, ?)",
            (filename, category_id),
        )
        self.conn.commit()

    def get_categories_for(self, filename: str) -> List[str]:
        cur = self.conn.cursor()
        rows = cur.execute(
            """
            SELECT c.name FROM categories c
            JOIN lora_category_map m ON c.id = m.category_id
            WHERE m.filename = ?
            ORDER BY c.name
            """,
            (filename,),
        ).fetchall()
        return [r[0] for r in rows]

    def search_by_category(self, category_id: int, query: str = "*") -> List[Dict[str, str]]:
        """Return LoRAs in ``category_id`` optionally filtered by a query."""
        cur = self.conn.cursor()
        if query == "*" or not query:
            rows = cur.execute(
                """
                SELECT l.filename, l.name, l.architecture, l.tags, l.base_model
                FROM lora_index l
                JOIN lora_category_map m ON l.filename = m.filename
                WHERE m.category_id = ?
                """,
                (category_id,),
            ).fetchall()
        else:
            rows = cur.execute(
                """
                SELECT l.filename, l.name, l.architecture, l.tags, l.base_model
                FROM lora_index l
                JOIN lora_category_map m ON l.filename = m.filename
                WHERE m.category_id = ? AND l MATCH ?
                """,
                (category_id, query),
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
