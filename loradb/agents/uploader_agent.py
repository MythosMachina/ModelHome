from pathlib import Path
from typing import Iterable

import shutil

from .. import config

class UploaderAgent:
    """Handle uploading LoRA files and preview images."""

    def __init__(self, upload_dir: Path | None = None) -> None:
        self.upload_dir = Path(upload_dir or config.UPLOAD_DIR)
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    def save_file(self, filename: str, fileobj) -> Path:
        """Save a single file and return its path."""
        dest = self.upload_dir / filename
        with dest.open("wb") as f:
            shutil.copyfileobj(fileobj, f)
        return dest
