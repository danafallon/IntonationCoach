"""Models and database functions for Intonation Coach project."""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

#######################################################################################
# Model definitions





#######################################################################################
# Helper functions

def connect_to_db(app):
	"""Connect the database to the Flask app."""

	app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dbname.db' 	# put in actual db name once created
	db.app = app
	db.init_app(app)

if __name__ == "__main__":
	# Allow for running this module interactively

	from server import app
	connect_to_db(app)
	print "Connected to DB."