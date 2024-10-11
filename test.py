from unittest import TestCase
from app import app
from flask import session
from boggle import Boggle


class FlaskTests(TestCase):

    def setUp(self):
        """stuff tp do before every test."""
        app.config['TESTING'] = True
        app.config['DEBUG_TB_HOSTS'] = ['dont-show-debug-toolbar']
        self.client = app.test_client()

    def test_index(self):
        """Test that the index page renders correctly and sets up to the session"""

        with self.client as client:
            response = client.get('/')
            self.assertEqual(response.status_code, 200)
            self.assertIn('board', session) # check if board stored in the session
            self.assertIn('possible_words', session) # check if possible_words are in session
            # self.assertIn('Boogle', response.data) #check if template renders "Boogle Game" in HTML

    def test_check_word_valid(self):
        """test chicking a valid word on the board."""

        with self.client as client:
            with client.session_transaction() as sess:
                sess['board'] = [
                    ["C", "A", "T", "S", "M"],
                    ["D", "O", "G", "R", "B"],
                    ["T", "R", "E", "E", "S"],
                    ["M", "O", "N", "K", "E"],
                    ["L", "A", "P", "S", "S"],
                ]

            response = client.get('/check-word?word=dog')
            self.assertEqual(response.json['result'], 'ok')


    def test_check_word_not_on_board(self):
        """test checking a word that exists in the dic but isn't on the board"""

        with self.client as client:
            client.get('/')

            with client.session_transaction() as sess:
                sess['board'] = [
                    ["C", "A", "T", "S", "M"],
                    ["D", "O", "G", "R", "B"],
                    ["T", "R", "E", "E", "S"],
                    ["M", "O", "N", "K", "E"],
                    ["L", "A", "P", "S", "S"],
                ]

                response = client.get('/check-word?word=apple')
                self.assertEqual(response.json['result'], 'not-on-board')
    def test_check_word_invalid(self):
        """Test checking an invalid word that is not in the dictionary."""

        with self.client as client:
            with client.session_transaction() as sess:
                sess['board'] = [
                    ["C", "A", "T", "S", "M"],
                    ["D", "O", "G", "R", "B"],
                    ["T", "R", "E", "E", "S"],
                    ["M", "O", "N", "K", "E"],
                    ["L", "A", "P", "S", "S"],
                ]

            response = client.get('/check-word?word=xyz')
            self.assertEqual(response.json['result'], 'not-word')


    def test_get_hint(self):
        """test getting a hint from the possible words"""

        with self.client as client:
            with client.session_transaction() as sess:
                sess['possible_words'] = ['dog', 'cat', 'tree']

            response = client.get('/get-hint')
            self.assertIn(response.json['hint'], ['dog', 'cat', 'tree'])


    def test_post_score(self):
        """test postinf a score and update the high score."""

        with self.client as client:
            with client.session_transaction() as sess:
                sess['highscore'] = 10
                sess['nplays'] = 1


                response = client.post('/post-score', json={"score": 15})
                self.assertEqual(response.json['new_highscore'], True) # new highscore achived
                with client.session_transaction() as sess:
                    self.assertEqual(sess['highscore'], 15)
                    self.assertEqual(sess['nplays'], 1)
        

