import unittest
from unittest.mock import patch

from flask import Flask, session
from flask_appbuilder import AppBuilder, SQLA
from flask_appbuilder.security.manager import AUTH_CAS


class CASTestCase(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)

        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///'
        self.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        self.app.config['SECRET_KEY'] = 'thisismyscretkey'
        self.app.config['AUTH_TYPE'] = AUTH_CAS
        self.app.config['CAS_SERVER'] = 'http://cas.server.com'

        self.db = SQLA(self.app)
        self.appbuilder = AppBuilder(self.app, self.db.session)

    def tearDown(self):
        self.appbuilder = None
        self.app = None
        self.db = None

    def test_login_by_logged_out_user(self):
        client = self.app.test_client()
        rv = client.get('/login/')
        self.assertEqual(rv.status_code, 302)
        self.assertEqual(
            rv.headers['Location'],
            'http://cas.server.com/login?service=http%3A%2F%2Flocalhost%2Flogin%2F'
        )

    @patch('flask_appbuilder.security.views.AuthCASView.validate', return_value={
        'username': 'casuser',
        'attributes': {
            'credentialType': 'UsernamePasswordCredential',
            'isFromNewLogin': 'true',
            'authenticationDate': '2019-05-21T01:36:51.967Z[UTC]',
            'authenticationMethod': 'QueryDatabaseAuthenticationHandler',
            'successfulAuthenticationHandlers': 'QueryDatabaseAuthenticationHandler',
            'longTermAuthenticationRequestTokenUsed': 'false'
        }
    })
    def test_login_by_logged_in_already(self, mock_validate):
        ticket = 'ticket-cas'
        self.app.config['AUTH_USER_REGISTRATION'] = True
        with self.app.test_client() as client:
            # cas callback login success
            client.get('/login/?ticket={0}'.format(ticket))

            rv = client.get('/login/')
            self.assertEqual(rv.status_code, 302)
            self.assertEqual(
                rv.headers['Location'],
                'http://localhost/'
            )

    @patch('flask_appbuilder.security.views.AuthCASView.validate', return_value={})
    def test_login_by_username_not_exists(self, mock_validate):
        ticket = 'ticket-cas'
        with self.app.test_client() as client:
            with client.session_transaction() as s:
                s[self.appbuilder.sm.cas_token_session_key] = ticket
            rv = client.get('/login/')
            self.assertEqual(rv.status_code, 403)

    @patch('flask_appbuilder.security.views.AuthCASView.validate', return_value={
        'username': 'casuser',
        'attributes': {
            'credentialType': 'UsernamePasswordCredential',
            'isFromNewLogin': 'true',
            'authenticationDate': '2019-05-21T01:36:51.967Z[UTC]',
            'authenticationMethod': 'QueryDatabaseAuthenticationHandler',
            'successfulAuthenticationHandlers': 'QueryDatabaseAuthenticationHandler',
            'longTermAuthenticationRequestTokenUsed': 'false'
        }
    })
    def test_login_by_cas_valid(self, mock_validate):
        ticket = 'ticket-cas'
        self.app.config['AUTH_USER_REGISTRATION'] = True
        with self.app.test_client() as client:
            rv = client.get('/login/?ticket={0}'.format(ticket))
            self.assertEqual(rv.status_code, 302)
            self.assertEqual(
                rv.headers['Location'],
                'http://localhost/')
            self.assertEqual(
                session.get(self.appbuilder.sm.cas_token_session_key),
                ticket)

    @patch('flask_appbuilder.security.views.AuthCASView.validate', return_value={
        'username': 'casuser',
        'attributes': {
            'credentialType': 'UsernamePasswordCredential',
            'isFromNewLogin': 'true',
            'authenticationDate': '2019-05-21T01:36:51.967Z[UTC]',
            'authenticationMethod': 'QueryDatabaseAuthenticationHandler',
            'successfulAuthenticationHandlers': 'QueryDatabaseAuthenticationHandler',
            'longTermAuthenticationRequestTokenUsed': 'false'
        }
    })
    def test_login_by_cas_valid_for_not_registration(self, mock_validate):
        ticket = 'ticket-cas'
        self.app.config['AUTH_USER_REGISTRATION'] = False
        with self.app.test_client() as client:
            rv = client.get('/login/?ticket={0}'.format(ticket))
            self.assertEqual(rv.status_code, 403)

    @patch('flask_appbuilder.security.views.AuthCASView.validate', return_value=None)
    def test_login_by_cas_invalid(self, mock_validate):
        ticket = 'ticket-cas'
        with self.app.test_client() as client:
            rv = client.get('/login/?ticket={0}'.format(ticket))
            self.assertEqual(rv.status_code, 302)
            self.assertEqual(
                rv.headers['Location'],
                'http://cas.server.com/login?service=http%3A%2F%2Flocalhost%2Flogin%2F')

    def test_logout(self):
        self.app.config['CAS_AFTER_LOGOUT'] = 'http://localhost:5000'
        with self.app.test_client() as client:
            rv = client.get('/logout/')
            self.assertEqual(rv.status_code, 302)
            self.assertEqual(
                rv.headers['Location'],
                'http://cas.server.com/logout?service=http%3A%2F%2Flocalhost%3A5000'
            )
            self.assertTrue(self.appbuilder.sm.cas_token_session_key not in session)
            self.assertTrue(self.appbuilder.sm.cas_username_session_key not in session)
            self.assertTrue(self.appbuilder.sm.cas_attributes_session_key not in session)

    @patch('cas.CASClientV2.verify_ticket', return_value=(
        'casuser',
        {'credentialType': 'UsernamePasswordCredential',
         'isFromNewLogin': 'true',
         'authenticationDate': '2019-05-20T09:17:53.368Z[UTC]',
         'authenticationMethod': 'QueryDatabaseAuthenticationHandler',
         'successfulAuthenticationHandlers': 'QueryDatabaseAuthenticationHandler',
         'longTermAuthenticationRequestTokenUsed': 'false'},
        None
    ))
    def test_validate_valid(self, mock_verify_ticket):
        ticket = 'ticket-cas'
        self.app.config['AUTH_USER_REGISTRATION'] = True
        with self.app.test_client() as client:
            rv = client.get('/login/?ticket={0}'.format(ticket))
            self.assertEqual(rv.status_code, 302)
            self.assertEqual(
                rv.headers['Location'],
                'http://localhost/')
            self.assertEqual(
                session.get(self.appbuilder.sm.cas_token_session_key),
                ticket)

    @patch('cas.CASClientV2.verify_ticket', return_value=(None, None, None))
    def test_validate_invalid(self, mock_verify_ticket):
        ticket = 'ticket-cas'
        with self.app.test_client() as client:
            rv = client.get('/login/?ticket={0}'.format(ticket))
            self.assertEqual(rv.status_code, 302)
            self.assertEqual(
                rv.headers['Location'],
                'http://cas.server.com/login?service=http%3A%2F%2Flocalhost%2Flogin%2F')
            self.assertTrue(
                self.appbuilder.sm.cas_token_session_key not in session)
