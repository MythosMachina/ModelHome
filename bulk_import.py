from __future__ import annotations

import argparse
from pathlib import Path
import shutil
from typing import Iterable, Dict, List, Optional

from safetensors import safe_open

from loradb.agents import IndexingAgent, UploaderAgent


def load_category_map(cat_dir: Path) -> Dict[str, List[str]]:
    """Return mapping of LoRA filenames to categories."""
    mapping: Dict[str, List[str]] = {}
    if not cat_dir:
        return mapping
    if not cat_dir.exists():
        return mapping
    for txt in cat_dir.glob("*.txt"):
        category = txt.stem
        with txt.open("r", encoding="utf-8") as f:
            lines = [ln.strip() for ln in f.read().splitlines() if ln.strip()]
        for name in lines:
            if not name.endswith(".safetensors"):
                name += ".safetensors"
            mapping.setdefault(name, []).append(category)
    return mapping


def extract_metadata(path: Path) -> dict[str, str]:
    """Read metadata from a safetensors file without requiring torch."""
    metadata = {"filename": path.name}
    try:
        with safe_open(str(path), framework=None) as f:
            meta = f.metadata() or {}
            metadata.update(meta)
    except Exception as exc:  # pragma: no cover - best effort
        metadata["error"] = str(exc)
    return metadata


def import_loras(
    safe_dir: Path,
    img_dir: Path,
    uploader: UploaderAgent,
    indexer: IndexingAgent,
    category_map: Optional[Dict[str, List[str]]] = None,
) -> None:
    """Walk ``safe_dir`` and import all ``.safetensors`` files found."""
    for st_file in safe_dir.rglob("*.safetensors"):
        # copy LoRA file
        with st_file.open("rb") as fh:
            dest = uploader.save_file(st_file.name, fh)
        meta = extract_metadata(dest)
        indexer.add_metadata(meta)
        if category_map and st_file.name in category_map:
            for cat in category_map[st_file.name]:
                cid = indexer.create_category(cat)
                indexer.assign_category(dest.name, cid)

        # copy associated previews
        rel = st_file.relative_to(safe_dir).with_suffix("")
        preview_dir = img_dir / rel
        if not preview_dir.is_dir():
            continue
        index = 0
        for img in sorted(preview_dir.iterdir()):
            if img.suffix.lower() not in {".png", ".jpg", ".jpeg", ".gif"}:
                continue
            if index == 0:
                dest_name = f"{st_file.stem}{img.suffix.lower()}"
            else:
                dest_name = f"{st_file.stem}_{index}{img.suffix.lower()}"
            dest_path = uploader.upload_dir / dest_name
            counter = 1
            while dest_path.exists():
                dest_path = uploader.upload_dir / f"{dest_path.stem}_{counter}{dest_path.suffix}"
                counter += 1
            shutil.copyfile(img, dest_path)
            index += 1


def main() -> None:
    parser = argparse.ArgumentParser(description="Bulk import LoRA files and previews")
    parser.add_argument("safetensors", type=Path, help="Directory with .safetensors files")
    parser.add_argument("images", type=Path, help="Directory with preview folders")
    parser.add_argument(
        "categories",
        type=Path,
        nargs="?",
        help="Optional directory with category text files",
    )
    args = parser.parse_args()

    uploader = UploaderAgent()
    indexer = IndexingAgent()

    cat_map = load_category_map(args.categories) if args.categories else {}
    import_loras(args.safetensors, args.images, uploader, indexer, cat_map)


if __name__ == "__main__":  # pragma: no cover - script entry
    main()
