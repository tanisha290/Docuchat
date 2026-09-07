import os

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS

from config import MAX_UPLOAD_SIZE_MB, DATABASE_URI
from database import init_db
from routes.documents import documents_bp
from routes.conversations import conversations_bp
from routes.chat import chat_bp

FRONTEND_DIST = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..", "frontend", "dist")
)


def create_app():
    app = Flask(__name__)
    CORS(app)  # allow the Vite dev server to call this API during development

    app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.config["MAX_CONTENT_LENGTH"] = MAX_UPLOAD_SIZE_MB * 1024 * 1024

    init_db(app)

    app.register_blueprint(documents_bp)
    app.register_blueprint(conversations_bp)
    app.register_blueprint(chat_bp)

    @app.route("/api/health", methods=["GET"])
    def health():
        return jsonify({"status": "ok"})

    @app.route("/", defaults={"path": ""})
    @app.route("/<path:path>")
    def serve_frontend(path):
        if path.startswith("api"):
            return jsonify({"error": "Not found."}), 404
        if os.path.isdir(FRONTEND_DIST):
            file_path = os.path.join(FRONTEND_DIST, path)
            if path and os.path.isfile(file_path):
                return send_from_directory(FRONTEND_DIST, path)
            index_path = os.path.join(FRONTEND_DIST, "index.html")
            if os.path.isfile(index_path):
                return send_from_directory(FRONTEND_DIST, "index.html")
        return jsonify({"error": "Not found."}), 404

    @app.errorhandler(413)
    def too_large(e):
        return jsonify({"error": f"File exceeds the {MAX_UPLOAD_SIZE_MB}MB limit."}), 413

    @app.errorhandler(500)
    def server_error(e):
        return jsonify({"error": "Internal server error."}), 500

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5000)
