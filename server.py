"""Server for Intonation Coach."""

from flask import Flask, render_template, session, send_from_directory, request, jsonify
from flask_debugtoolbar import DebugToolbarExtension
import jinja2
import json
import base64
from os import path

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

@app.route('/english-us')
def english_content():
	"""Display US English page."""

	return render_template('english-us.html')


@app.route('/russian')
def russian_content():
	"""Display Russian page."""

	return render_template('russian.html')


@app.route('/<path:path>')
def send_audio_file(path):
	"""Given a url of an audio file, return that file as stored in static folder."""

	return send_from_directory('static', path)


@app.route('/targetdata', methods=["POST"])
def send_target_pitch_data():
	"""Sends pitch data from target recording to be displayed in graph when page loads."""

	target_filepath = request.form.get("sentence") + "_pd.json"
	target_file = open(target_filepath)
	target_json = json.loads(target_file.read())
	target_pitch_data = json.dumps(target_json, sort_keys=True)
	print type(target_pitch_data)
	target_file.close()

	return jsonify(target=target_pitch_data)


@app.route('/analyze', methods=["POST"])
def analyze_user_rec():
	"""Analyze the user's recording and send pitch data for both recordings back to page."""

	# # fetch target recording's pitch data:
	# target_filepath = request.form.get("sentence") + "_pd.json"
	# target_file = open(target_filepath)
	# target_json = json.loads(target_file.read())
	# target_pitch_data = json.dumps(target_json, sort_keys=True)
	# # print type(target_pitch_data)
	# target_file.close()

	# analyze user's recording:
	user_b64 = request.form.get("user_rec")[22:]
	user_wav = base64.b64decode(user_b64)
	f = open('user-rec.wav', 'wb')
	f.write(user_wav)
	f.close()
	user_rec_filepath = path.abspath('user-rec.wav')

	user_pitch_data = format_pitch_data(praat_analyze_pitch(user_rec_filepath))
	return jsonify(user=user_pitch_data)



if __name__ == "__main__":
	app.debug = True
	# connect_to_db(app)

	DebugToolbarExtension(app)
	app.run()
