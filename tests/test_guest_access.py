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


def test_guest_showcase_detail_access():
    os.environ.pop("TESTING", None)
    resp = client.get("/showcase_detail/test.safetensors")
    assert resp.status_code == 200
    assert "Download" not in resp.text
    assert "metadata-table" not in resp.text
    os.environ["TESTING"] = "1"


def test_custom_404_page():
    os.environ["TESTING"] = "1"
    resp = client.get("/no_such_page", headers={"accept": "text/html"})
    assert resp.status_code == 404
    assert "/static/404.jpg" in resp.text


def test_access_denied_page_for_user():
    os.environ.pop("TESTING", None)
    import sqlite3
    main.app.state.auth.conn.close()
    main.app.state.auth.conn = sqlite3.connect(
        main.app.state.auth.db_path, check_same_thread=False
    )
    main.app.state.auth._ensure_table()
    main.app.state.auth.create_user("regular", "secret", role="user")
    client.post("/login", data={"username": "regular", "password": "secret"})
    resp = client.get("/admin/users", headers={"accept": "text/html"})
    assert resp.status_code == 403
    assert "Permission, you have not" in resp.text
    assert "/static/accessdenied.jpg" in resp.text
    os.environ["TESTING"] = "1"
