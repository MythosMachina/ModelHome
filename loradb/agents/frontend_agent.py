from pathlib import Path
from typing import List, Dict
import random

from jinja2 import Environment, FileSystemLoader


class FrontendAgent:
    """Render HTML views for the LoRA gallery using Bootstrap."""

    def __init__(self, uploads_dir: Path, template_dir: Path) -> None:
        self.uploads_dir = uploads_dir
        self.env = Environment(loader=FileSystemLoader(template_dir))
        # Cache mapping a file stem to the list of preview URLs
        self.preview_cache: Dict[str, List[str]] = {}

    def _find_previews(self, stem: str) -> List[str]:
        """Return preview URLs for ``stem`` using a simple cache."""
        if stem in self.preview_cache:
            return self.preview_cache[stem]
        # Include numbered variants like "name_1.png" as well as the base
        patterns = [
            f"{stem}.png",
            f"{stem}.jpg",
            f"{stem}_*.png",
            f"{stem}_*.jpg",
        ]
        matches: List[str] = []
        for pattern in patterns:
            matches.extend([str(p) for p in self.uploads_dir.glob(pattern)])
        urls = [f"/uploads/{Path(m).name}" for m in matches]
        self.preview_cache[stem] = urls
        return urls

    def invalidate_preview_cache(self, stem: str | None = None) -> None:
        """Remove ``stem`` from the preview cache or clear it entirely."""
        if stem is None:
            self.preview_cache.clear()
        else:
            self.preview_cache.pop(stem, None)

    def refresh_preview_cache(self, stem: str) -> List[str]:
        """Force re-scan of previews for ``stem`` and return the result."""
        self.invalidate_preview_cache(stem)
        return self._find_previews(stem)

    def render_grid(
        self,
        entries: List[Dict[str, str]],
        query: str | None = None,
        categories: List[Dict[str, str]] | None = None,
        selected_category: str | None = None,
        limit: int = 50,
    ) -> str:
        for e in entries:
            stem = Path(e.get("filename", "")).stem
            previews = self._find_previews(stem)
            e["preview_url"] = random.choice(previews) if previews else None
        template = self.env.get_template("grid.html")
        return template.render(
            title="LoRA Gallery",
            entries=entries,
            query=query or "",
            categories=categories or [],
            selected_category=selected_category or "",
            limit=limit,
        )

    def render_detail(
        self, entry: Dict[str, str], categories: List[Dict[str, str]] | None = None
    ) -> str:
        stem = Path(entry.get("filename", "")).stem
        previews = self._find_previews(stem)
        entry["previews"] = previews
        entry.setdefault("metadata", {})
        template = self.env.get_template("detail.html")
        return template.render(title=entry.get("name"), entry=entry, categories=categories or [])

    def render_category_admin(self, categories: List[Dict[str, str]]) -> str:
        """Render the category administration page."""
        template = self.env.get_template("category_admin.html")
        return template.render(title="Category Administration", categories=categories)
