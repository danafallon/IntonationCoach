"""Server for Intonation Coach."""

from flask import Flask, render_template, session
from flask_debugtoolbar import DebugToolbarExtension
import jinja2

import model
from pitchgraph import praat_analyze_pitch, format_pitch_data


app = Flask(__name__)

app.secret_key = 'this-should-be-something-unguessable'

app.jinja_env.undefined = jinja2.StrictUndefined



@app.route('/')
def index():
	"""Homepage. User will choose language here."""

	return render_template("home.html")


@app.route('/about')
def about():
	"""Show the about page."""

	return render_template("about.html")


@app.route('/french')
def french_content():
	"""Display explanation text and sample sentences, with play buttons for sample recordings."""

	return render_template("french.html")


@app.route('/analyze')
def analyze_user_rec():
	"""Analyze the user's recording and send pitch data back to page."""

	user_audio = request.form.get("user_file")
	user_pitch_data = format_pitch_data(praat_analyze_pitch(user_audio))
	return user_pitch_data



if __name__ == "__main__":
	app.debug = True
	# connect_to_db(app)

	DebugToolbarExtension(app)
	app.run()
