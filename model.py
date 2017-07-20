import json

from flask_sqlalchemy import SQLAlchemy
from werkzeug import generate_password_hash, check_password_hash


db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(254), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime)

    def __repr__(self):
        return "<User %s>" % self.email

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Recording(db.Model):
    """User recording, containing both the audio data and the json pitch data."""

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('recordings', lazy=True))
    ex_id = db.Column(db.String(15), nullable=False)
    attempt_num = db.Column(db.Integer, nullable=False)
    audio_data = db.Column(db.String(4000000))
    pitch_data = db.Column(db.String(1000000))
    created_at = db.Column(db.DateTime)

    def __repr__(self):
        return "<Recording %s: user %s, %s, attempt %s>" % (self.id, self.user_id,
                                                            self.ex_id, self.attempt_num)

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "ex_id": self.ex_id,
            "attempt_num": self.attempt_num,
            "audio_data": self.audio_data,
            "pitch_data": json.loads(self.pitch_data)
        }


def connect_to_db(app):
    db.app = app
    db.init_app(app)


if __name__ == "__main__":
    # Allow for running this module interactively
    from application import application
    connect_to_db(application)
    print "Connected to DB."
