import os
import sys
import types
import pytest
from fastapi.testclient import TestClient

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import main
import loradb.api as api

client = TestClient(main.app)

def setup_module(module):
    # Stub indexer methods to avoid database usage
    api.indexer.assign_category = lambda filename, cid: None
    api.indexer.unassign_category = lambda filename, cid: None

def test_assign_category_valid_redirect():
    response = client.post(
        "/assign_category",
        data={"filename": "model.safetensors", "category_id": "1"},
        headers={"accept": "text/html"},
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert response.headers["location"] == "/detail/model.safetensors"

def test_assign_category_invalid_filename():
    response = client.post(
        "/assign_category",
        data={"filename": "http://evil.com", "category_id": "1"},
        headers={"accept": "text/html"},
        follow_redirects=False,
    )
    assert response.status_code == 400

def test_unassign_category_invalid_filename():
    response = client.post(
        "/unassign_category",
        data={"filename": "../secret.safetensors", "category_id": "1"},
        headers={"accept": "text/html"},
        follow_redirects=False,
    )
    assert response.status_code == 400
