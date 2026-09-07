"""
API-level tests using Flask's test client. These don't hit the real
Gemini API — they check routing, validation, and error handling only.
Run with: pytest backend/tests/test_api.py
"""
import io
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest  # noqa: E402
from app import create_app  # noqa: E402
from database import db  # noqa: E402


@pytest.fixture
def client():
    app = create_app()
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    with app.app_context():
        db.create_all()
        with app.test_client() as c:
            yield c
        db.drop_all()


def test_health(client):
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "ok"


def test_upload_rejects_non_pdf(client):
    data = {"file": (io.BytesIO(b"not a pdf"), "notes.txt")}
    resp = client.post("/api/documents/upload", data=data, content_type="multipart/form-data")
    assert resp.status_code == 400
    assert "PDF" in resp.get_json()["error"]


def test_upload_requires_file(client):
    resp = client.post("/api/documents/upload", data={}, content_type="multipart/form-data")
    assert resp.status_code == 400


def test_list_documents_empty(client):
    resp = client.get("/api/documents")
    assert resp.status_code == 200
    assert resp.get_json()["documents"] == []


def test_create_conversation_without_document(client):
    resp = client.post("/api/conversations", json={})
    assert resp.status_code == 201
    body = resp.get_json()["conversation"]
    assert body["document_id"] is None


def test_create_conversation_missing_document_404(client):
    resp = client.post("/api/conversations", json={"document_id": 9999})
    assert resp.status_code == 404


def test_get_missing_conversation_404(client):
    resp = client.get("/api/conversations/9999")
    assert resp.status_code == 404


def test_send_message_to_missing_conversation_404(client):
    resp = client.post("/api/conversations/9999/messages", json={"content": "hi"})
    assert resp.status_code == 404


def test_send_empty_message_rejected(client):
    conv_resp = client.post("/api/conversations", json={})
    conv_id = conv_resp.get_json()["conversation"]["id"]
    resp = client.post(f"/api/conversations/{conv_id}/messages", json={"content": "   "})
    assert resp.status_code == 400
