from pathlib import Path
from typing import Iterable, List
import tempfile
import zipfile

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

    def save_preview_zip(self, zip_file) -> List[Path]:
        """Save and extract a zip of preview images for a LoRA."""
        stem = Path(zip_file.filename).stem
        extracted: List[Path] = []
        with tempfile.TemporaryDirectory() as td:
            temp_path = Path(td) / zip_file.filename
            with open(temp_path, "wb") as f:
                shutil.copyfileobj(zip_file.file, f)
            with zipfile.ZipFile(temp_path) as zf:
                index = 0
                for info in zf.infolist():
                    if info.is_dir():
                        continue
                    suffix = Path(info.filename).suffix.lower()
                    if suffix not in {".png", ".jpg", ".jpeg", ".gif"}:
                        continue
                    if index == 0:
                        dest_name = f"{stem}{suffix}"
                    else:
                        dest_name = f"{stem}_{index}{suffix}"
                    dest = self.upload_dir / dest_name
                    with zf.open(info) as src, dest.open("wb") as out:
                        shutil.copyfileobj(src, out)
                    extracted.append(dest)
                    index += 1
        return extracted

    def delete_lora(self, filename: str) -> None:
        """Delete a LoRA file and all associated preview images."""
        path = self.upload_dir / filename
        if path.exists():
            path.unlink()
        stem = Path(filename).stem
        for ext in [".png", ".jpg", ".jpeg", ".gif"]:
            for p in self.upload_dir.glob(f"{stem}*{ext}"):
                p.unlink(missing_ok=True)

    def delete_preview(self, filename: str) -> None:
        """Delete a single preview image."""
        path = self.upload_dir / filename
        if path.exists():
            path.unlink()
