import unittest

import sys
from os import path
sys.path.append(path.dirname(path.dirname( path.abspath(__file__) )))

from pitchgraph import praat_analyze_pitch, format_pitch_data


class PitchgraphTestCase(unittest.TestCase):
	"""Tests for 'pitchgraph.py'."""

	def test_something(self):
		pass


if __name__ == "__main__":
    unittest.main()