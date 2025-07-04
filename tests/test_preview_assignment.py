import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
os.environ["TESTING"] = "1"

from loradb.agents.frontend_agent import FrontendAgent


def test_preview_filtering(tmp_path):
    # Create some preview files for two different LoRAs
    (tmp_path / "Mizuki.png").write_text("a")
    (tmp_path / "Mizuki_18.png").write_text("a")
    (tmp_path / "Mizuki_Furui_SDXL_10.png").write_text("a")

    agent = FrontendAgent(tmp_path, Path("loradb/templates"))
    previews = agent._find_previews("Mizuki")

    assert "/uploads/Mizuki.png" in previews
    assert "/uploads/Mizuki_18.png" in previews
    assert "/uploads/Mizuki_Furui_SDXL_10.png" not in previews
