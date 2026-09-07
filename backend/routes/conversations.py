from flask import Blueprint, request, jsonify

from database import db
from models import Conversation, Document

conversations_bp = Blueprint("conversations", __name__)


@conversations_bp.route("/api/conversations", methods=["POST"])
def create_conversation():
    data = request.get_json(silent=True) or {}
    document_id = data.get("document_id")

    if document_id is not None:
        document = Document.query.get(document_id)
        if not document:
            return jsonify({"error": "Document not found."}), 404

    conversation = Conversation(document_id=document_id, title=data.get("title"))
    db.session.add(conversation)
    db.session.commit()
    return jsonify({"conversation": conversation.to_dict()}), 201


@conversations_bp.route("/api/conversations", methods=["GET"])
def list_conversations():
    conversations = Conversation.query.order_by(Conversation.created_at.desc()).all()
    return jsonify({"conversations": [c.to_dict() for c in conversations]})


@conversations_bp.route("/api/conversations/<int:conversation_id>", methods=["GET"])
def get_conversation(conversation_id):
    conversation = Conversation.query.get(conversation_id)
    if not conversation:
        return jsonify({"error": "Conversation not found."}), 404
    return jsonify({"conversation": conversation.to_dict(include_messages=True)})
