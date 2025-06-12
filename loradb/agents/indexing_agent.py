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
