import os
import sys
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# Disable testing shortcut to exercise the middleware during these tests
ORIG_TESTING = os.environ.pop("TESTING", None)

import main

client = TestClient(main.app)


def test_guest_showcase_access():
    os.environ.pop("TESTING", None)
    resp = client.get("/showcase")
    assert resp.status_code == 200
    assert "Model Showcase" in resp.text
    os.environ["TESTING"] = "1"


def test_guest_redirect_to_showcase():
    os.environ.pop("TESTING", None)
    resp = client.get("/grid")
    assert resp.history and resp.history[0].status_code == 307
    assert resp.url.path == "/showcase"
    os.environ["TESTING"] = "1"
