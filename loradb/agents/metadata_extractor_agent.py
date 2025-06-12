from pathlib import Path
from typing import Dict

from safetensors import safe_open

class MetadataExtractorAgent:
    """Extract metadata from LoRA files."""

    def extract(self, filepath: Path) -> Dict[str, str]:
        """Extract basic metadata from a safetensors file."""
        metadata = {"filename": filepath.name}
        try:
            with safe_open(str(filepath), framework="pt") as f:
                meta = f.metadata() or {}
                metadata.update(meta)
                keys = list(f.keys())
                metadata["tensor_keys"] = ",".join(keys)
        except Exception as exc:
            metadata["error"] = str(exc)
        return metadata
