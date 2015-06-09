import unittest

import sys
from os import path
sys.path.append(path.dirname(path.dirname( path.abspath(__file__) )))

from pitchgraph import praat_analyze_pitch, format_pitch_data


class PitchgraphTestCase(unittest.TestCase):
	"""Tests for 'pitchgraph.py'."""

	def test_analyze_pitch_returns_dict(self):
		"""Does praat_analyze_pitch return a dict?"""
		audio_file = path.abspath('static/sounds/en-us-1.wav')
		self.assertIsInstance(praat_analyze_pitch(audio_file), dict)

	def test_data_smoothing(self):
		"""Does format_pitch_data """


if __name__ == "__main__":
    unittest.main()