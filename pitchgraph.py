from praatinterface import PraatLoader
from os import path
import json
from operator import itemgetter

def praat_analyze_pitch(audio_file):
	"""Given a wav file, use Praat to return a dictionary containing pitch (in Hz)
	at each millisecond."""

	praatpath = path.abspath('Praat.app/Contents/MacOS/Praat')	# locate Praat executable
	pl = PraatLoader(praatpath=praatpath)	# create instance of PraatLoader object
	
	praat_output = pl.run_script('pitch.praat', audio_file)	# run pitch script in Praat
	pitch_data = pl.read_praat_out(praat_output) # turn Praat's output into Python dict

	return pitch_data


def format_pitch_data(pd):
	"""Clean up the dictionary returned by praatinterface, put it in the format
	needed for graphing, smooth data by reducing number of datapoints, and return it as JSON."""

	for t in pd.keys():
		pd[t] = pd[t]['Pitch'] 	  # make each value just the pitch, instead of a sub-dict
		if pd[t] == 0:
			del pd[t]		  # if pitch is 0, remove from dictionary

	# now, pd is dict where each key is time (x value) and each value is pitch (y value)
	# to format for graph input, make list of dicts containing x-y pairs
	datapoints_list = []
	for t in pd.keys():
		datapoint = {}
		datapoint["x"] = t
		datapoint["y"] = pd[t]
		datapoints_list.append(datapoint)

	# sort the list by the value of "x"
	datapoints_sorted = sorted(datapoints_list, key=itemgetter("x"))

	# with this sorted list, do some data smoothing
	# pull out every nth item
	i = 0
	datapoints_keep = []
	while i < len(datapoints_sorted):
		datapoints_keep.append(datapoints_sorted[i])
		i += 50
	# make sure last item is included so length of curve isn't lost
	datapoints_keep.append(datapoints_sorted[-1])

	# print "num of datapoints:", len(datapoints_keep)
	# print datapoints_keep[:100]

	return json.dumps(datapoints_keep, sort_keys=True)


if __name__ == "__main__":
	audio_file = path.abspath('./static/sounds/fr-5.wav')
	pitch_data = praat_analyze_pitch(audio_file)
	json_pd = format_pitch_data(pitch_data)
	print json_pd

	

