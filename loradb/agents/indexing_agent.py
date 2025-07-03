from typing import Dict, List
import math

import sqlite3
from pathlib import Path

import config
from .metadata_extractor_agent import MetadataExtractorAgent

class IndexingAgent:
    """Maintain search index for LoRA metadata using SQLite FTS5."""

    #: ID used for the dynamic "no category" entry returned by
    #: :py:meth:`list_categories`.
    NO_CATEGORY_ID = 0
    #: Display name for the dynamic "no category" entry.
    NO_CATEGORY_NAME = "No Category"

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

    def _uncategorized_exists(self) -> bool:
        """Return ``True`` if any LoRA has no category assigned."""
        cur = self.conn.cursor()
        cur.execute(
            """
            SELECT 1 FROM lora_index l
            LEFT JOIN lora_category_map m ON l.filename = m.filename
            WHERE m.filename IS NULL
            LIMIT 1
            """
        )
        return cur.fetchone() is not None

    # --- Statistics helpers ----------------------------------------------

    def lora_count(self) -> int:
        """Return the total number of indexed LoRA files."""
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*) FROM lora_index")
        return int(cur.fetchone()[0])

    def category_count(self) -> int:
        """Return the number of categories, including the dynamic one."""
        cur = self.conn.cursor()
        cur.execute("SELECT COUNT(*) FROM categories")
        count = int(cur.fetchone()[0])
        if self._uncategorized_exists():
            count += 1
        return count

    def preview_count(self) -> int:
        """Return the number of preview images stored in the uploads folder."""
        uploads = Path(config.UPLOAD_DIR)
        if not uploads.exists():
            return 0
        exts = ["*.png", "*.jpg", "*.jpeg", "*.gif"]
        return sum(len(list(uploads.glob(p))) for p in exts)

    def top_categories(self, limit: int = 10) -> List[Dict[str, str]]:
        """Return ``limit`` categories with the most assigned LoRAs."""
        cur = self.conn.cursor()
        rows = cur.execute(
            """
            SELECT c.id, c.name, COUNT(m.filename) AS cnt
            FROM categories c
            LEFT JOIN lora_category_map m ON c.id = m.category_id
            GROUP BY c.id
            ORDER BY cnt DESC, c.name
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
        categories = [
            {"id": r[0], "name": r[1], "count": int(r[2])}
            for r in rows
        ]
        # Insert uncategorised entry if required
        cur.execute(
            """
            SELECT COUNT(*) FROM lora_index l
            LEFT JOIN lora_category_map m ON l.filename = m.filename
            WHERE m.filename IS NULL
            """
        )
        uncategorised = int(cur.fetchone()[0])
        if uncategorised:
            categories.append(
                {
                    "id": self.NO_CATEGORY_ID,
                    "name": self.NO_CATEGORY_NAME,
                    "count": uncategorised,
                }
            )
        # Sort again to ensure uncategorised slot is in correct position
        categories.sort(key=lambda c: c["count"], reverse=True)
        categories = categories[:limit]

        # Calculate relative font sizes for the category cloud
        if categories:
            weights = [math.log(c["count"] + 1) for c in categories]
            min_w = min(weights)
            max_w = max(weights)
            span = max_w - min_w or 1
            min_size = 0.8
            max_size = 2.0
            for c, w in zip(categories, weights):
                rel = (w - min_w) / span
                size = min_size + rel * (max_size - min_size)
                c["size"] = round(size, 2)

        return categories

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

    def search(
        self,
        query: str,
        limit: int | None = None,
        offset: int = 0,
    ) -> List[Dict[str, str]]:
        cur = self.conn.cursor()
        if query == "*":
            sql = "SELECT filename, name, architecture, tags, base_model FROM lora_index"
            params = []
        else:
            sql = (
                "SELECT filename, name, architecture, tags, base_model FROM lora_index WHERE lora_index MATCH ?"
            )
            params = [query]
        if limit is not None:
            sql += " LIMIT ? OFFSET ?"
            params.extend([limit, offset])
        elif offset:
            sql += " LIMIT -1 OFFSET ?"
            params.append(offset)
        rows = cur.execute(sql, params).fetchall()
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
        categories = [{"id": r[0], "name": r[1]} for r in rows]
        if self._uncategorized_exists():
            categories.insert(0, {"id": self.NO_CATEGORY_ID, "name": self.NO_CATEGORY_NAME})
        return categories

    def list_categories_with_counts(self) -> List[Dict[str, str]]:
        """Return categories along with the number of assigned LoRAs."""
        cur = self.conn.cursor()
        rows = cur.execute(
            """
            SELECT c.id, c.name, COUNT(m.filename) AS cnt
            FROM categories c
            LEFT JOIN lora_category_map m ON c.id = m.category_id
            GROUP BY c.id
            ORDER BY c.name
            """
        ).fetchall()
        categories = [
            {"id": r[0], "name": r[1], "count": int(r[2])}
            for r in rows
        ]
        cur.execute(
            """
            SELECT COUNT(*) FROM lora_index l
            LEFT JOIN lora_category_map m ON l.filename = m.filename
            WHERE m.filename IS NULL
            """
        )
        uncategorised = int(cur.fetchone()[0])
        if uncategorised:
            categories.insert(
                0,
                {
                    "id": self.NO_CATEGORY_ID,
                    "name": self.NO_CATEGORY_NAME,
                    "count": uncategorised,
                },
            )
        return categories

    def delete_category(self, category_id: int) -> None:
        """Delete a category and its assignments."""
        self.conn.execute("DELETE FROM categories WHERE id = ?", (category_id,))
        self.conn.execute(
            "DELETE FROM lora_category_map WHERE category_id = ?",
            (category_id,),
        )
        self.conn.commit()

    def assign_category(self, filename: str, category_id: int) -> None:
        self.conn.execute(
            "INSERT OR IGNORE INTO lora_category_map(filename, category_id) VALUES (?, ?)",
            (filename, category_id),
        )
        self.conn.commit()

    def unassign_category(self, filename: str, category_id: int) -> None:
        """Remove ``filename`` from the given ``category_id`` mapping."""
        self.conn.execute(
            "DELETE FROM lora_category_map WHERE filename = ? AND category_id = ?",
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
        names = [r[0] for r in rows]
        if not names:
            names.append(self.NO_CATEGORY_NAME)
        return names

    def get_categories_with_ids(self, filename: str) -> List[Dict[str, str]]:
        """Return categories for ``filename`` including the category IDs."""
        cur = self.conn.cursor()
        rows = cur.execute(
            """
            SELECT c.id, c.name FROM categories c
            JOIN lora_category_map m ON c.id = m.category_id
            WHERE m.filename = ?
            ORDER BY c.name
            """,
            (filename,),
        ).fetchall()
        if rows:
            return [{"id": r[0], "name": r[1]} for r in rows]
        return [{"id": self.NO_CATEGORY_ID, "name": self.NO_CATEGORY_NAME}]

    def search_by_category(
        self,
        category_id: int,
        query: str = "*",
        limit: int | None = None,
        offset: int = 0,
    ) -> List[Dict[str, str]]:
        """Return LoRAs in ``category_id`` optionally filtered by a query."""
        cur = self.conn.cursor()
        if category_id == self.NO_CATEGORY_ID:
            if query == "*" or not query:
                sql = (
                    "SELECT l.filename, l.name, l.architecture, l.tags, l.base_model "
                    "FROM lora_index l LEFT JOIN lora_category_map m ON l.filename = m.filename "
                    "WHERE m.filename IS NULL"
                )
                params: List = []
            else:
                sql = (
                    "SELECT l.filename, l.name, l.architecture, l.tags, l.base_model "
                    "FROM lora_index l LEFT JOIN lora_category_map m ON l.filename = m.filename "
                    "WHERE m.filename IS NULL AND l MATCH ?"
                )
                params = [query]
        else:
            if query == "*" or not query:
                sql = (
                    "SELECT l.filename, l.name, l.architecture, l.tags, l.base_model "
                    "FROM lora_index l JOIN lora_category_map m ON l.filename = m.filename "
                    "WHERE m.category_id = ?"
                )
                params = [category_id]
            else:
                sql = (
                    "SELECT l.filename, l.name, l.architecture, l.tags, l.base_model "
                    "FROM lora_index l JOIN lora_category_map m ON l.filename = m.filename "
                    "WHERE m.category_id = ? AND l MATCH ?"
                )
                params = [category_id, query]
        if limit is not None:
            sql += " LIMIT ? OFFSET ?"
            params.extend([limit, offset])
        elif offset:
            sql += " LIMIT -1 OFFSET ?"
            params.append(offset)
        rows = cur.execute(sql, params).fetchall()
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

    # --- Additional helpers for dashboard --------------------------------

    def storage_volume(self) -> int:
        """Return the total size in bytes of all LoRA files."""
        uploads = Path(config.UPLOAD_DIR)
        total = 0
        if uploads.exists():
            for p in uploads.glob("*.safetensors"):
                try:
                    total += p.stat().st_size
                except OSError:
                    pass
        return total

    def recent_loras(self, limit: int = 5) -> List[Dict[str, str]]:
        """Return most recently indexed LoRAs."""
        cur = self.conn.cursor()
        rows = cur.execute(
            "SELECT filename, name FROM lora_index ORDER BY rowid DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [
            {"filename": r[0], "name": r[1]} for r in rows
        ]

    def recent_categories(self, limit: int = 5) -> List[Dict[str, str]]:
        """Return categories ordered by most recent assignment or creation."""
        cur = self.conn.cursor()
        rows = cur.execute(
            """
            SELECT c.id, c.name, MAX(COALESCE(m.rowid, c.id)) AS last_id
            FROM categories c
            LEFT JOIN lora_category_map m ON c.id = m.category_id
            GROUP BY c.id
            ORDER BY last_id DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
        return [
            {"id": r[0], "name": r[1]} for r in rows
        ]
