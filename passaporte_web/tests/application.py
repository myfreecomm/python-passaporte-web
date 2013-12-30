# -*- coding: utf-8 -*-
import unittest

import requests
import api_toolkit
from helpers import use_cassette as use_pw_cassette

from passaporte_web.main import Application, Account, Identity
from passaporte_web.tests.helpers import TEST_USER, APP_CREDENTIALS

__all__ = ['ApplicationTest', 'ApplicationUsersTest']

class ApplicationTest(unittest.TestCase):

    def setUp(self):
        with use_pw_cassette('application/collections_options'):
            self.app = Application(**APP_CREDENTIALS)

    def test_instance_has_accounts_and_users(self):
        self.assertTrue(hasattr(self.app, 'accounts'))
        self.assertTrue(isinstance(self.app.accounts, api_toolkit.Collection))

        self.assertTrue(hasattr(self.app, 'users'))
        self.assertTrue(isinstance(self.app.users, api_toolkit.Collection))

    def test_application_accounts_are_a_collection(self):
        with use_pw_cassette('application/account_list'):
            app_accounts = list(self.app.accounts.all())

        self.assertEquals(len(app_accounts), 26)
        for item in app_accounts:
            self.assertTrue(isinstance(item, Account))

    def test_application_accounts_cannot_be_deleted(self):
        with use_pw_cassette('application/account_list'):
            first_account = self.app.accounts.all().next()

        self.assertRaises(ValueError, first_account.delete)

    def test_application_accounts_cannot_be_updated(self):
        with use_pw_cassette('application/account_list'):
            first_account = self.app.accounts.all().next()

        self.assertRaises(ValueError, first_account.save)


class ApplicationUsersTest(unittest.TestCase):

    def setUp(self):
        with use_pw_cassette('application/collections_options'):
            self.app = Application(**APP_CREDENTIALS)

    def test_application_users_are_not_iterable(self):
        app_users = self.app.users.all()
        self.assertRaises(ValueError, app_users.next)

    def test_application_users_can_be_created(self):
        user_data = {
            'first_name': 'Myfc ID',
            'last_name': 'Clients',
            'email': TEST_USER['email'],
            'password': TEST_USER['password'],
            'password2': TEST_USER['password'],
            'tos': True,
        }

        with use_pw_cassette('user/registration_success'):
            user = self.app.users.create(**user_data)

        self.assertTrue(isinstance(user, Identity))

    def test_application_users_must_be_created_with_correct_data(self):
        user_data = {
            'first_name': 'Myfc ID',
            'last_name': 'Clients',
            'email': TEST_USER['email'],
            'password': TEST_USER['password'],
            'tos': True,
        }

        with use_pw_cassette('user/registration_failure_one_password'):
            self.assertRaises(requests.HTTPError, self.app.users.create ,**user_data)

    def test_application_must_have_permissions_to_create_users(self):
        user_data = {
            'first_name': 'Myfc ID',
            'last_name': 'Clients',
            'email': TEST_USER['email'],
            'password': TEST_USER['password'],
            'password2': TEST_USER['password'],
            'tos': True,
        }

        with use_pw_cassette('user/registration_failure_app_without_permissions'):
            self.assertRaises(requests.HTTPError, self.app.users.create ,**user_data)

    def test_user_email_must_be_unique(self):
        user_data = {
            'first_name': 'Myfc ID',
            'last_name': 'Clients',
            'email': TEST_USER['email'],
            'password': TEST_USER['password'],
            'password2': TEST_USER['password'],
            'tos': True,
        }

        with use_pw_cassette('user/registration_failure_duplicated_email'):
            self.assertRaises(requests.HTTPError, self.app.users.create ,**user_data)

    def test_user_cpf_must_be_unique(self):
        user_data = {
            'first_name': 'Myfc ID',
            'last_name': 'Clients',
            'email': TEST_USER['email'],
            'password': TEST_USER['password'],
            'password2': TEST_USER['password'],
            'cpf': '11111111111',
            'tos': True,
        }

        with use_pw_cassette('user/registration_failure_duplicated_cpf'):
            self.assertRaises(requests.HTTPError, self.app.users.create ,**user_data)

    def test_user_cpf_must_be_valid(self):
        user_data = {
            'first_name': 'Myfc ID',
            'last_name': 'Clients',
            'email': TEST_USER['email'],
            'password': TEST_USER['password'],
            'password2': TEST_USER['password'],
            'cpf': '1111111111111111111',
            'tos': True,
        }

        with use_pw_cassette('user/registration_failure_invalid_cpf'):
            self.assertRaises(requests.HTTPError, self.app.users.create ,**user_data)

    def test_user_must_agree_with_tos(self):
        user_data = {
            'first_name': 'Myfc ID',
            'last_name': 'Clients',
            'email': TEST_USER['email'],
            'password': TEST_USER['password'],
            'password2': TEST_USER['password'],
        }

        with use_pw_cassette('user/registration_failure_missing_tos'):
            self.assertRaises(requests.HTTPError, self.app.users.create ,**user_data)

    def test_user_passwords_must_match(self):
        user_data = {
            'first_name': 'Myfc ID',
            'last_name': 'Clients',
            'email': TEST_USER['email'],
            'password': TEST_USER['password'],
            'password2': 'will not match',
            'tos': True,
        }

        with use_pw_cassette('user/registration_failure_password_mismatch'):
            self.assertRaises(requests.HTTPError, self.app.users.create ,**user_data)

    def test_get_user_by_email(self):
        with use_pw_cassette('user/get_by_email'):
            user = self.app.users.get(email=TEST_USER['email'])

        self.assertTrue(isinstance(user, Identity))
        self.assertEquals(user.email, TEST_USER['email'])

    def test_get_user_by_email_fails_when_email_is_not_registered(self):
        with use_pw_cassette('user/get_by_unknown_email'):
            self.assertRaises(requests.HTTPError, self.app.users.get, email='notregistered@test.example')

    def test_get_user_by_uuid(self):
        with use_pw_cassette('user/get_by_uuid'):
            user = self.app.users.get(uuid=TEST_USER['uuid'])

        self.assertTrue(isinstance(user, Identity))
        self.assertEquals(user.email, TEST_USER['email'])

    def test_get_user_by_uuid_fails_when_uuid_is_not_registered(self):
        with use_pw_cassette('user/get_by_unknown_uuid'):
            self.assertRaises(requests.HTTPError, self.app.users.get, uuid='001')

    def test_application_must_have_permission_to_get_user(self):
        with use_pw_cassette('user/get_without_permission'):
            self.assertRaises(requests.HTTPError, self.app.users.get, uuid=TEST_USER['uuid'])

    def test_get_by_unknown_parameter_raises_TypeError(self):
        self.assertRaises(TypeError, self.app.users.get, first_name='Myfc ID')

    def test_authenticate_user_with_email_and_password(self):
        with use_pw_cassette('user/authenticate_with_email_and_password'):
            user = self.app.users.authenticate(email=TEST_USER['email'], password=TEST_USER['password'])
        
        self.assertTrue(isinstance(user, Identity))
        self.assertEquals(user.uuid, TEST_USER['uuid'])

    def test_authenticate_user_with_id_token(self):
        with use_pw_cassette('user/authenticate_with_id_token'):
            user = self.app.users.authenticate(id_token=TEST_USER['id_token'])
        
        self.assertTrue(isinstance(user, Identity))
        self.assertEquals(user.uuid, TEST_USER['uuid'])

    def test_user_credentials_are_replaced_by_app_credentials_in_session(self):
        with use_pw_cassette('user/authenticate_with_email_and_password'):
            user = self.app.users.authenticate(email=TEST_USER['email'], password=TEST_USER['password'])
        
        self.assertEquals(user._session.auth, (
            APP_CREDENTIALS['token'], APP_CREDENTIALS['secret']
        ))
