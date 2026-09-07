import json
from datetime import datetime

from database import db


class Document(db.Model):
    __tablename__ = "documents"

    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    upload_date = db.Column(db.DateTime, default=datetime.utcnow)
    file_path = db.Column(db.String(500), nullable=False)
    index_path = db.Column(db.String(500), nullable=True)
    num_pages = db.Column(db.Integer, default=0)
    num_chunks = db.Column(db.Integer, default=0)
    status = db.Column(db.String(50), default="processing")  # processing | ready | failed
    error_message = db.Column(db.Text, nullable=True)

    conversations = db.relationship(
        "Conversation", backref="document", cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "filename": self.filename,
            "upload_date": self.upload_date.isoformat() if self.upload_date else None,
            "num_pages": self.num_pages,
            "num_chunks": self.num_chunks,
            "status": self.status,
            "error_message": self.error_message,
        }


class Conversation(db.Model):
    __tablename__ = "conversations"

    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey("documents.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    title = db.Column(db.String(255), nullable=True)

    messages = db.relationship(
        "Message", backref="conversation", cascade="all, delete-orphan",
        order_by="Message.timestamp",
    )

    def to_dict(self, include_messages=False):
        data = {
            "id": self.id,
            "document_id": self.document_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "title": self.title,
        }
        if include_messages:
            data["messages"] = [m.to_dict() for m in self.messages]
        return data


class Message(db.Model):
    __tablename__ = "messages"

    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey("conversations.id"), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # "user" | "assistant"
    content = db.Column(db.Text, nullable=False)
    sources = db.Column(db.Text, nullable=True)  # JSON string: [{"document":..,"page":..}]
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "conversation_id": self.conversation_id,
            "role": self.role,
            "content": self.content,
            "sources": json.loads(self.sources) if self.sources else [],
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
        }
