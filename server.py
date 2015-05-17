"""Server for Intonation Coach."""

from flask import Flask, render_template, session, send_from_directory
from flask_debugtoolbar import DebugToolbarExtension
import jinja2
import json

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


@app.route('/sounds/<path:filename>')
def send_audio_file(filename):
    return send_from_directory('static/sounds', filename)

@app.route('/analyze')
def analyze_user_rec():
	"""Analyze the user's recording and send pitch data for both recordings back to page."""

	# fetch target recording's pitch data:
	target_filepath = request.form.get("sentence") + "_pd.json"
	target_file = open(target_filepath)
	target_pitch_data = json.loads(target_file.read())

	# analyze user's recording:
	user_audio = request.form.get("user_file")
	user_pitch_data = format_pitch_data(praat_analyze_pitch(user_audio))
	return [target_pitch_data, user_pitch_data]



if __name__ == "__main__":
	app.debug = True
	# connect_to_db(app)

	DebugToolbarExtension(app)
	app.run()
