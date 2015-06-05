import unittest

import sys, os
from os import path
sys.path.append(path.dirname(path.dirname( path.abspath(__file__) )))
import server

import tempfile


class ServerTestCase(unittest.TestCase):
	"""Tests for 'server.py'."""

	def setUp(self):
		self.db_fd, server.app.config['DATABASE'] = tempfile.mkstemp()
		server.app.config['TESTING'] = True
		self.app = server.app.test_client()

	def tearDown(self):
		os.close(self.db_fd)
		os.unlink(server.app.config['DATABASE'])

	def test_renders_english_template(self):
		res = self.app.get('/')
		self.assertIn('English (US)', res.data)

	# @unittest.skip('skip for now')
	def test_send_audio_file(self):
		res = self.app.get('/sounds/en-us-1.wav')
		self.assertIs(res.status_code, 200)
		


if __name__ == "__main__":
    unittest.main()