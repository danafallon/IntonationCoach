import json
from operator import itemgetter
from os import path

from praatinterface import PraatLoader


def get_praat_pitch(audio_file):
    """Given a wav file, use Praat to return a dictionary containing pitch (in Hz)
    at each millisecond."""

    pl = PraatLoader(praatpath=path.abspath('Praat.app/Contents/MacOS/Praat'))
    praat_output = pl.run_script('pitch.praat', audio_file)
    pitch_data = pl.read_praat_out(praat_output)

    return pitch_data


def format_pitch_data(pitch_data):
    """Put pitch data in the format needed for graphing."""

    datapoints = [{"x": time, "y": meta['Pitch']} for time, meta in pitch_data.iteritems()]

    return sorted(datapoints, key=itemgetter("x"))


def smooth_pitch_data(datapoints):
    """Thin out data set to allow for b-spline smoothing in chart, and return as JSON."""

    i = 0
    datapoints_keep = []
    if datapoints:
        # reduce number of datapoints per second from 1000 to 20, remove points with pitch of zero
        while i < len(datapoints):
            point = datapoints[i]
            if point["y"]:
                datapoints_keep.append(point)
            i += 50
        # make sure last item is included so length of curve isn't lost
        datapoints_keep.append(datapoints[-1])

    return json.dumps(datapoints_keep, sort_keys=True)


def analyze_pitch(audio_file):
    """Run full pitch analysis."""

    return smooth_pitch_data(format_pitch_data(get_praat_pitch(audio_file)))


if __name__ == "__main__":
    print analyze_pitch(path.abspath('./static/sounds/fr-5.wav'))
