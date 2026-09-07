import json

from flask import Blueprint, request, jsonify

from database import db
from models import Conversation, Document, Message
from rag.rag_engine import answer_question

chat_bp = Blueprint("chat", __name__)


@chat_bp.route("/api/conversations/<int:conversation_id>/messages", methods=["GET"])
def get_messages(conversation_id):
    conversation = Conversation.query.get(conversation_id)
    if not conversation:
        return jsonify({"error": "Conversation not found."}), 404
    return jsonify({"messages": [m.to_dict() for m in conversation.messages]})


@chat_bp.route("/api/conversations/<int:conversation_id>/messages", methods=["POST"])
def send_message(conversation_id):
    conversation = Conversation.query.get(conversation_id)
    if not conversation:
        return jsonify({"error": "Conversation not found."}), 404

    data = request.get_json(silent=True) or {}
    question = (data.get("content") or "").strip()
    if not question:
        return jsonify({"error": "Message content cannot be empty."}), 400

    # Optional override: ask across multiple documents in one turn.
    document_ids = data.get("document_ids")

    user_message = Message(conversation_id=conversation_id, role="user", content=question)
    db.session.add(user_message)
    db.session.commit()

    history = [m.to_dict() for m in conversation.messages if m.id != user_message.id]

    filename_lookup = {}
    target_document_id = conversation.document_id
    if document_ids:
        docs = Document.query.filter(Document.id.in_(document_ids)).all()
        filename_lookup = {d.id: d.filename for d in docs}
    elif target_document_id:
        document = Document.query.get(target_document_id)
        if document:
            filename_lookup = {document.id: document.filename}

    try:
        result = answer_question(
            question=question,
            document_id=target_document_id if not document_ids else None,
            document_ids=document_ids,
            history_messages=history,
            filename_lookup=filename_lookup,
        )
    except Exception as e:  # noqa: BLE001
        return jsonify({"error": f"Failed to generate an answer: {e}"}), 500

    # Attach filenames to sources for single-document mode too.
    single_doc_name = None
    if target_document_id and not document_ids:
        doc = Document.query.get(target_document_id)
        single_doc_name = doc.filename if doc else None
    for s in result["sources"]:
        if s.get("document") is None:
            s["document"] = single_doc_name

    assistant_message = Message(
        conversation_id=conversation_id,
        role="assistant",
        content=result["answer"],
        sources=json.dumps(result["sources"]),
    )
    db.session.add(assistant_message)

    if not conversation.title:
        conversation.title = question[:80]

    db.session.commit()

    return jsonify({
        "answer": result["answer"],
        "sources": result["sources"],
        "message": assistant_message.to_dict(),
    })
