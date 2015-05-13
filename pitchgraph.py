from praatinterface import PraatLoader
from os import path

def praat_analyze_pitch(audio_file):
	"""Given a wav file, use Praat to return a dictionary containing pitch (in Hz)
	at each millisecond."""

	praatpath = path.abspath('Praat.app/Contents/MacOS/Praat')	# locate Praat executable
	pl = PraatLoader(praatpath=praatpath)	# create instance of PraatLoader object
	
	praat_output = pl.run_script('pitch.praat', audio_file)	# run pitch script in Praat
	pitch_data = pl.read_praat_out(praat_output) # turn Praat's output into Python dict

	return pitch_data


def format_pitch_data(pd):
	"""Clean up the dictionary returned by praatinterface."""

	for t in pd.keys():
		pd[t] = pd[t]['Pitch'] 	  # make each value just the pitch, instead of a sub-dict
		if pd[t] == 0:
			pd[t] = None		  # if pitch is 0, replace with None

	return pd


if __name__ == "__main__":
	audio_file = path.abspath('supermarche2.wav')
	pitch_data = praat_analyze_pitch(audio_file)
	formatted_data = format_pitch_data(pitch_data)
	for key in sorted(formatted_data):		
		print key, ": ", formatted_data[key]		# display keys and values in order (for me)























