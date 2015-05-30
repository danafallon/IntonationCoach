"""Models and database functions for Intonation Coach project."""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

#######################################################################################
# Model definitions

class Recording(db.Model):
	"""User recording, containing both the audio data and the json pitch data."""

	__tablename__ = "Recordings"

	rec_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
	ex_id = db.Column(db.String(15), nullable=False)
	attempt_num = db.Column(db.Integer, nullable=False)
	audio_data = db.Column(db.String(4000000))
	pitch_data = db.Column(db.String(1000000))

	def __repr__(self):
		return "<Recording rec_id=%s ex_id=%s attempt_num=%s>" % (self.rec_id, self.ex_id, self.attempt_num)

	def serialize(self):
		"""Return recording object in easily serializable format so that it can be jsonified."""

		serialized = {
			"rec_id": self.rec_id,
			"ex_id": self.ex_id,
			"attempt_num": self.attempt_num,
			"audio_data": self.audio_data,
			"pitch_data": self.pitch_data
		}

		return serialized



#######################################################################################
# Helper functions

def connect_to_db(app):
	"""Connect the database to the Flask app."""

	app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///recordings.db'
	db.app = app
	db.init_app(app)


if __name__ == "__main__":
	# Allow for running this module interactively

	from server import app
	connect_to_db(app)
	print "Connected to DB."