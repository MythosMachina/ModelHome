from pathlib import Path
from typing import Iterable, List

import shutil

import config

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

    def save_files(self, files: Iterable) -> List[Path]:
        """Save multiple uploaded files."""
        saved: List[Path] = []
        for file in files:
            name = Path(file.filename).name
            dest = self.upload_dir / name
            # Ensure unique destination
            counter = 1
            while dest.exists():
                dest = self.upload_dir / f"{dest.stem}_{counter}{dest.suffix}"
                counter += 1
            with dest.open("wb") as f:
                shutil.copyfileobj(file.file, f)
            saved.append(dest)
        return saved
