"""Intonation Coach"""

from flask import Flask, render_template, session

from model import *		# pass in names explicitly later


app = Flask(__name__)














if __name__ == "__main__":
	app.run(debug=True)
	connect_to_db(app)
	app.run()
