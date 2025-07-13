import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from loradb.agents.indexing_agent import IndexingAgent


def test_exact_filename_lookup(tmp_path):
    db = tmp_path / "index.db"
    indexer = IndexingAgent(db_path=db)

    indexer.add_metadata({"filename": "ChillinDifferentWorld_Blossom.safetensors"})
    indexer.add_metadata({"filename": "Blossom.safetensors"})

    entry = indexer.get_entry("Blossom.safetensors")
    assert entry is not None
    assert entry["filename"] == "Blossom.safetensors"
