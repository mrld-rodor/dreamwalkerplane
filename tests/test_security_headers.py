import unittest

from flask import Flask

from control.security import configure_proxy, configure_security


class SecurityHeadersTestCase(unittest.TestCase):
    def setUp(self):
        app = Flask(__name__)
        app.config['SECRET_KEY'] = 'test-secret'
        app.config['TESTING'] = True
        app.config['ENABLE_HSTS'] = False

        configure_proxy(app)
        configure_security(app)

        @app.route('/')
        def index():
            return 'ok'

        self.app = app
        self.client = app.test_client()

    def test_required_headers_present_on_http(self):
        response = self.client.get('/')

        self.assertEqual(response.headers.get('X-Frame-Options'), 'SAMEORIGIN')
        self.assertEqual(response.headers.get('X-XSS-Protection'), '1; mode=block')
        self.assertEqual(response.headers.get('X-Content-Type-Options'), 'nosniff')
        self.assertEqual(response.headers.get('Referrer-Policy'), 'strict-origin-when-cross-origin')
        self.assertIn('default-src', response.headers.get('Content-Security-Policy', ''))
        self.assertIsNone(response.headers.get('Strict-Transport-Security'))

    def test_hsts_present_on_https_when_enabled(self):
        self.app.config['ENABLE_HSTS'] = True

        response = self.client.get('/', base_url='https://example.com')

        self.assertEqual(
            response.headers.get('Strict-Transport-Security'),
            'max-age=31536000; includeSubDomains'
        )


if __name__ == '__main__':
    unittest.main()