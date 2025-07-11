import io
import os
import sys
from types import SimpleNamespace

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from loradb.agents.uploader_agent import UploaderAgent


class DummyFile(SimpleNamespace):
    def __init__(self, filename: str, data: bytes = b"test"):
        super().__init__(filename=filename, file=io.BytesIO(data))


def test_duplicate_lora_rejected(tmp_path):
    agent = UploaderAgent(upload_dir=tmp_path)
    agent.save_files([DummyFile("model.safetensors")])
    with pytest.raises(FileExistsError):
        agent.save_files([DummyFile("model.safetensors")])
