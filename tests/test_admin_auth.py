import unittest

from flask import Flask
from werkzeug.security import generate_password_hash

from control.admin_auth import verify_admin_credentials


class AdminAuthTestCase(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'test-secret'
        self.app.config['TESTING'] = True
        self.app.config['ADMIN_USERNAME'] = 'admin'

    def test_accepts_password_hash_when_configured(self):
        self.app.config['ADMIN_PASSWORD_HASH'] = generate_password_hash('senha-segura')
        self.app.config['ADMIN_PASSWORD'] = 'senha-antiga'

        with self.app.app_context():
            self.assertTrue(verify_admin_credentials('admin', 'senha-segura'))
            self.assertFalse(verify_admin_credentials('admin', 'senha-antiga'))

    def test_falls_back_to_plaintext_password(self):
        self.app.config['ADMIN_PASSWORD'] = 'senha-legada'
        self.app.config['ADMIN_PASSWORD_HASH'] = ''

        with self.app.app_context():
            self.assertTrue(verify_admin_credentials('admin', 'senha-legada'))
            self.assertFalse(verify_admin_credentials('admin', 'senha-incorreta'))

    def test_rejects_wrong_username(self):
        self.app.config['ADMIN_PASSWORD_HASH'] = generate_password_hash('senha-segura')

        with self.app.app_context():
            self.assertFalse(verify_admin_credentials('outro', 'senha-segura'))


if __name__ == '__main__':
    unittest.main()