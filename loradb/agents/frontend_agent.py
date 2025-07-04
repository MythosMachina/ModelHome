import random
import re
from pathlib import Path
from typing import Dict, List

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
        # Only match files for this exact stem. We allow either an exact
        # filename match (``<stem>.png``) or a numeric suffix
        # (``<stem>_1.png``). Previous glob patterns like ``<stem>_*.png``
        # would also match names such as ``<stem>_other.png`` which belongs to
        # a different LoRA. Use a regular expression to avoid such collisions.
        pattern = re.compile(
            rf"^{re.escape(stem)}(?:_[0-9]+)?\.(?:png|jpg)$", re.IGNORECASE
        )
        matches: List[str] = []
        for p in self.uploads_dir.iterdir():
            if pattern.match(p.name):
                matches.append(str(p))
        urls = [f"/uploads/{Path(m).name}" for m in sorted(matches)]
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
        user: Dict[str, str] | None = None,
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
            user=user,
        )

    def render_showcase(
        self, entries: List[Dict[str, str]], user: Dict[str, str] | None = None
    ) -> str:
        """Render the public showcase grid."""
        for e in entries:
            stem = Path(e.get("filename", "")).stem
            previews = self._find_previews(stem)
            e["preview_url"] = random.choice(previews) if previews else None
        template = self.env.get_template("showcase.html")
        return template.render(title="Model Showcase", entries=entries, user=user)

    def render_detail(
        self,
        entry: Dict[str, str],
        categories: List[Dict[str, str]] | None = None,
        user: Dict[str, str] | None = None,
    ) -> str:
        stem = Path(entry.get("filename", "")).stem
        previews = self._find_previews(stem)
        entry["previews"] = previews
        entry.setdefault("metadata", {})
        template = self.env.get_template("detail.html")
        return template.render(
            title=entry.get("name"),
            entry=entry,
            categories=categories or [],
            user=user,
        )

    def render_category_admin(
        self, categories: List[Dict[str, str]], user: Dict[str, str] | None = None
    ) -> str:
        """Render the category administration page."""
        template = self.env.get_template("category_admin.html")
        return template.render(
            title="Category Administration",
            categories=categories,
            user=user,
        )

    def render_bulk_assign(
        self,
        files: List[str],
        categories: List[Dict[str, str]],
        user: Dict[str, str] | None = None,
    ) -> str:
        """Render form to assign multiple LoRAs to a category."""
        template = self.env.get_template("bulk_assign.html")
        return template.render(
            title="Add to Category",
            files=files,
            categories=categories,
            user=user,
        )

    def render_user_admin(
        self, users: List[Dict[str, str]], user: Dict[str, str] | None = None
    ) -> str:
        template = self.env.get_template("user_admin.html")
        return template.render(title="User Administration", users=users, user=user)
