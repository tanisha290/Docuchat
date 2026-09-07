from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def init_db(app):
    """Attach SQLAlchemy to the Flask app and create tables if they don't exist."""
    db.init_app(app)
    with app.app_context():
        db.create_all()
