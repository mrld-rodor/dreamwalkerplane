import unittest

from flask import Flask

from control.csrf import csrf_protect, generate_csrf_token, init_csrf


class CsrfProtectionTestCase(unittest.TestCase):
    def setUp(self):
        app = Flask(__name__)
        app.config['SECRET_KEY'] = 'test-secret'
        app.config['TESTING'] = True

        init_csrf(app)

        @app.route('/token')
        def token():
            return {'csrf_token': generate_csrf_token()}

        @app.route('/protected', methods=['POST'])
        @csrf_protect
        def protected():
            return 'ok'

        self.client = app.test_client()

    def test_missing_token_is_rejected(self):
        response = self.client.post('/protected')

        self.assertEqual(response.status_code, 400)

    def test_valid_token_is_accepted(self):
        token_response = self.client.get('/token')
        csrf_token = token_response.get_json()['csrf_token']

        response = self.client.post('/protected', data={'csrf_token': csrf_token})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_data(as_text=True), 'ok')


if __name__ == '__main__':
    unittest.main()