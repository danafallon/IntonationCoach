import os
import sys
import tempfile
import unittest

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import server


class ServerTestCase(unittest.TestCase):
    """Tests for server.py"""

    def setUp(self):
        self.db_fd, server.app.config['DATABASE'] = tempfile.mkstemp()
        server.app.config['TESTING'] = True
        self.app = server.app.test_client()

    def tearDown(self):
        os.close(self.db_fd)
        os.unlink(server.app.config['DATABASE'])

    def test_renders_english_template(self):
        """Does the English page load from the expected route?"""

        res = self.app.get('/english-us')
        self.assertIn('English (US)', res.data)
        self.assertIn('Overview', res.data)
        self.assertIn('Declarative', res.data)

    def test_renders_french_template(self):
        """Does the French page load at the expected route?"""

        res = self.app.get('/french')
        self.assertIn('French', res.data)
        self.assertIn('Overview', res.data)
        self.assertIn('Declarative', res.data)

    def test_send_audio_file(self):
        """Is an audio file successfully fetched from the static folder?"""

        res = self.app.get('/sounds/en-us-1.wav')
        self.assertIs(res.status_code, 200)

    @unittest.skip('')
    def test_send_target_pitch_data(self):
        """Is target pitch data being sent to the page?"""

        res = self.app.post('/targetdata', data=dict(sentence='en-us-1'))
        self.assertIsNotNone(res.data)


if __name__ == "__main__":
    unittest.main()
