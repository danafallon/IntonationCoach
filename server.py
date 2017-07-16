import json
import base64
import datetime
import os

from flask import (Flask, flash, jsonify, redirect, render_template, request,
                   send_from_directory, session, url_for)
import jinja2

from forms import LoginForm, SignupForm
from model import Recording, User, connect_to_db, db
from pitchgraph import analyze_pitch


app = Flask(__name__)
app.secret_key = 'development key'
app.jinja_env.undefined = jinja2.StrictUndefined


@app.route('/')
def index():
    return render_template("home.html")


@app.route('/signup', methods=["GET", "POST"])
def signup():
    form = SignupForm()

    if form.validate_on_submit():
        user = User(email=form.email.data.lower(), created_at=datetime.datetime.now())
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()

        session['user_id'] = user.id
        session['email'] = user.email
        return redirect(url_for('index'))

    elif form.errors:
        flash("Error creating account")

    return render_template("signup.html", form=form)


@app.route('/login', methods=["GET", "POST"])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            if user.check_password(form.password.data):
                session['user_id'] = user.id
                session['email'] = user.email
                return redirect(url_for('index'))
        flash('Invalid email or password')

    return render_template("login.html", form=form)


@app.route('/logout')
def logout():
    if 'user_id' in session:
        session.pop('user_id')
    if 'email' in session:
        session.pop('email')

    return redirect(url_for('login'))


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
        target_pitch_data = json.loads(target_file.read())

    attempts = []
    if 'user_id' in session:
        attempts = Recording.query.filter_by(user_id=session['user_id'], ex_id=ex_id).all()

    return jsonify(target_pitch_data=target_pitch_data,
                   attempts=[attempt.serialize() for attempt in attempts])


@app.route('/analyze', methods=["POST"])
def analyze_user_rec():
    """Analyze the user's recording, save audio data and pitch data to
    the database if they're logged in, and send pitch data back to page."""

    ex_id = request.form.get("ex_id")
    # cut off first 22 chars ("data:audio/wav;base64,")
    user_b64 = request.form.get("user_rec")[22:]
    user_wav = base64.b64decode(user_b64)
    user_recording_path = os.path.abspath('./static/sounds/user-rec.wav')
    with open(user_recording_path, 'wb') as f:
        f.write(user_wav)
    user_pitch_data = analyze_pitch(user_recording_path)

    attempt = {}
    if 'user_id' in session:
        attempts = Recording.query.filter_by(user_id=session['user_id'], ex_id=ex_id).all()
        attempt_num = 1
        if attempts:
            attempt_num += max(attempt.attempt_num for attempt in attempts)
        new_rec = Recording(user_id=session['user_id'],
                            ex_id=ex_id,
                            attempt_num=attempt_num,
                            audio_data=user_b64,
                            pitch_data=user_pitch_data,
                            created_at=datetime.datetime.now())
        db.session.add(new_rec)
        db.session.commit()
        attempt = new_rec.serialize()
    else:
        attempt = {
            "ex_id": ex_id,
            "audio_data": user_b64,
            "pitch_data": json.loads(user_pitch_data)
            }

    return jsonify(attempt=attempt)


@app.route('/delete-attempt', methods=["POST"])
def delete_attempt():
    rec = Recording.query.filter_by(id=request.form.get("id")).first()
    if rec:
        db.session.delete(rec)
        db.session.commit()

    return redirect(redirect_url())


def redirect_url(default='index'):
    return request.args.get('next') or request.referrer or url_for(default)


if __name__ == "__main__":
    app.debug = True
    connect_to_db(app)
    app.run()
