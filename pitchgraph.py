from praatinterface import PraatLoader
from os import path
import json
from operator import itemgetter

def get_praat_pitch(audio_file):
	"""Given a wav file, use Praat to return a dictionary containing pitch (in Hz)
	at each millisecond."""

	pl = PraatLoader(praatpath=path.abspath('Praat.app/Contents/MacOS/Praat'))
	praat_output = pl.run_script('pitch.praat', audio_file)
	pitch_data = pl.read_praat_out(praat_output)

	return pitch_data


def format_pitch_data(pitch_data):
	"""Clean up the dictionary returned by praatinterface and put it in the
	format needed for graphing."""

	for time in pitch_data.keys():
		# remove unnecessary sub-dicts
		pitch_data[time] = pitch_data[time]['Pitch']
		# ignore points with pitch of 0
		if pitch_data[time] == 0:
			del pitch_data[time]

	datapoints_list = []
	for time in pitch_data.keys():
		datapoints_list.append({
			"x": time,
			"y": pitch_data[time]
			})

	return sorted(datapoints_list, key=itemgetter("x"))
	

def smooth_pitch_data(datapoints_sorted):
	"""Thin out data set to allow for b-spline smoothing in chart, and return as JSON."""
	
	i = 0
	datapoints_keep = []

	# only smooth data if there is data (avoid index out of range error if no audio recorded)
	if datapoints_sorted:
		# reduce number of datapoints per second from 1000 to 20
		while i < len(datapoints_sorted):
			datapoints_keep.append(datapoints_sorted[i])
			i += 50
		# make sure last item is included so length of curve isn't lost
		datapoints_keep.append(datapoints_sorted[-1])

	return json.dumps(datapoints_keep, sort_keys=True)


def analyze_pitch(audio_file):
	"""Run full pitch analysis."""

	return smooth_pitch_data(format_pitch_data(get_praat_pitch(audio_file)))


if __name__ == "__main__":
	audio_file = path.abspath('./static/sounds/fr-5.wav')
	pitch_data = analyze_pitch(audio_file)
	print pitch_data

	

