import os
import uuid

from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename

from config import UPLOAD_DIR, ALLOWED_EXTENSIONS, MAX_UPLOAD_SIZE_MB
from database import db
from models import Document
from rag.pdf_processor import NoExtractableTextError
from rag.rag_engine import process_document
from rag.vector_store import delete_index

documents_bp = Blueprint("documents", __name__)


def _allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@documents_bp.route("/api/documents/upload", methods=["POST"])
def upload_document():
    if "file" not in request.files:
        return jsonify({"error": "No file part in the request."}), 400

    file = request.files["file"]
    if file.filename == "":
        return jsonify({"error": "No file selected."}), 400

    if not _allowed_file(file.filename):
        return jsonify({"error": "Only PDF files are supported."}), 400

    file.seek(0, os.SEEK_END)
    size_mb = file.tell() / (1024 * 1024)
    file.seek(0)
    if size_mb > MAX_UPLOAD_SIZE_MB:
        return jsonify({"error": f"File exceeds the {MAX_UPLOAD_SIZE_MB}MB limit."}), 400

    original_name = secure_filename(file.filename)
    stored_name = f"{uuid.uuid4().hex}_{original_name}"
    file_path = os.path.join(UPLOAD_DIR, stored_name)
    file.save(file_path)

    document = Document(filename=original_name, file_path=file_path, status="processing")
    db.session.add(document)
    db.session.commit()

    try:
        num_pages, num_chunks, index_path = process_document(document.id, file_path)
        document.num_pages = num_pages
        document.num_chunks = num_chunks
        document.index_path = index_path
        document.status = "ready"
        db.session.commit()
    except NoExtractableTextError as e:
        document.status = "failed"
        document.error_message = str(e)
        db.session.commit()
        return jsonify({"error": str(e), "document": document.to_dict()}), 422
    except Exception as e:  # noqa: BLE001
        document.status = "failed"
        document.error_message = f"Processing failed: {e}"
        db.session.commit()
        return jsonify({"error": document.error_message, "document": document.to_dict()}), 500

    return jsonify({"document": document.to_dict()}), 201


@documents_bp.route("/api/documents", methods=["GET"])
def list_documents():
    docs = Document.query.order_by(Document.upload_date.desc()).all()
    return jsonify({"documents": [d.to_dict() for d in docs]})


@documents_bp.route("/api/documents/<int:document_id>", methods=["DELETE"])
def delete_document(document_id):
    document = Document.query.get(document_id)
    if not document:
        return jsonify({"error": "Document not found."}), 404

    if document.file_path and os.path.exists(document.file_path):
        os.remove(document.file_path)
    delete_index(document.id)

    db.session.delete(document)
    db.session.commit()
    return jsonify({"deleted": document_id})
