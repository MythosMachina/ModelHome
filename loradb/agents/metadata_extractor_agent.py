from pathlib import Path
from typing import Dict

from safetensors import safe_open

class MetadataExtractorAgent:
    """Extract metadata from LoRA files."""

    def extract(self, filepath: Path, include_tensor_keys: bool = False) -> Dict[str, str]:
        """Extract basic metadata from a safetensors file.

        Parameters
        ----------
        filepath:
            The safetensors file to read metadata from.
        include_tensor_keys:
            Whether to include the list of tensor keys from the file. Disabled by
            default as these can be very large.
        """
        metadata = {"filename": filepath.name}
        try:
            with safe_open(str(filepath), framework="pt") as f:
                meta = f.metadata() or {}
                metadata.update(meta)
                if include_tensor_keys:
                    keys = list(f.keys())
                    metadata["tensor_keys"] = ",".join(keys)
        except Exception as exc:
            metadata["error"] = str(exc)
        return metadata
