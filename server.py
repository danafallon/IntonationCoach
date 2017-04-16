"""Server for Intonation Coach."""

from flask import (Flask, render_template, session, send_from_directory,
	request, jsonify, flash, redirect, url_for, Response)
from flask_debugtoolbar import DebugToolbarExtension
import jinja2
import json
import base64
from os import path

from model import Recording, connect_to_db, db
from pitchgraph import analyze_pitch


app = Flask(__name__)
app.secret_key = 'development key'
app.jinja_env.undefined = jinja2.StrictUndefined

response = Response()

@app.route('/')
def index():
	return render_template("home.html")


@app.route('/about')
def about():
	return render_template("about.html")


@app.route('/guidelines')
def guidelines():
	return render_template("guidelines.html")


@app.route('/french')
def french_content():
	return render_template("french.html")


@app.route('/english-us')
def english_content():
	return render_template('english-us.html')


@app.route('/russian')
def russian_content():
	return render_template('russian.html')


@app.route('/<path:path>')
def send_audio_file(path):
	return send_from_directory('static', path)


@app.route('/targetdata', methods=["POST"])
def send_target_pitch_data():
	"""Send pitch data from target recording to be displayed in graph when tab loads. 
	Also send the user's past attempts at this sentence, if any."""

	ex_id = request.form.get("sentence")
	with open("./static/json/" + ex_id + "-pd.json") as target_file:
		target_json = json.loads(target_file.read())
		target_pitch_data = json.dumps(target_json, sort_keys=True)

	attempts = Recording.query.filter_by(ex_id=ex_id).all() or []

	return jsonify(target=target_pitch_data,
				   attempts=[attempt.serialize() for attempt in attempts])


@app.route('/analyze', methods=["POST"])
def analyze_user_rec():
	"""Analyze the user's recording, save the audio data and pitch data to
	database, and send pitch data back to page."""

	# cut off first 22 chars ("data:audio/wav;base64,")
	user_b64 = request.form.get("user_rec")[22:]
	user_wav = base64.b64decode(user_b64)
	user_recording_path = path.abspath('./static/sounds/user-rec.wav')
	with open(user_recording_path, 'wb') as f:
		f.write(user_wav)
	
	user_pitch_data = analyze_pitch(user_recording_path)

	# store audio data (user_b64) and user_pitch_data in db
	ex_id = request.form.get("ex_id")
	attempts = Recording.query.filter_by(ex_id=ex_id).all()
	if attempts:
		attempt_num = max(attempt.attempt_num for attempt in attempts) + 1
	else:
		attempt_num = 1

	new_rec = Recording(ex_id=ex_id,
						attempt_num=attempt_num,
						audio_data=user_b64,
						pitch_data=user_pitch_data)
	db.session.add(new_rec)
	db.session.commit()

	return jsonify(user_pitch_data=user_pitch_data,
				   user_audio_data=json.dumps(user_b64),
				   rec_id=new_rec.rec_id)


@app.route('/delete-attempt', methods=["POST"])
def delete_attempt():
	rec_id = request.form.get("rec_id")
	rec = Recording.query.filter_by(rec_id=rec_id).one()
	db.session.delete(rec)
	db.session.commit()

	return redirect(redirect_url())


def redirect_url(default='index'):
    return request.args.get('next') or request.referrer or url_for(default)


if __name__ == "__main__":
	app.debug = True
	connect_to_db(app)
	# DebugToolbarExtension(app)
	app.run()
