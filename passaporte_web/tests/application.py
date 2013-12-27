# -*- coding: utf-8 -*-
from os import path
import unittest
from vcr import VCR

import requests
import api_toolkit
from helpers import use_cassette as use_pw_cassette

from passaporte_web.main import Application, Account, Identity

__all__ = ['ApplicationTest', 'ApplicationUsersTest']

TEST_CREDENTIALS = {
    'host': 'http://sandbox.app.passaporteweb.com.br',
    'token': 'qxRSNcIdeA',
    'secret': '1f0AVCZPJbRndF9FNSGMOWMfH9KMUDaX',
}
test_user_email = 'identity_client@disposableinbox.com'
test_user_password = '*SudN7%r$MiYRa!E'


class ApplicationTest(unittest.TestCase):

    def setUp(self):
        with use_pw_cassette('application/collections_options'):
            self.app = Application(**TEST_CREDENTIALS)

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

        self.assertRaises(ValueError, first_account.delete)


class ApplicationUsersTest(unittest.TestCase):

    def setUp(self):
        with use_pw_cassette('application/collections_options'):
            self.app = Application(**TEST_CREDENTIALS)

    def test_application_users_are_not_iterable(self):
        app_users = self.app.users.all()
        self.assertRaises(ValueError, app_users.next)

    def test_application_users_cannot_be_read(self):
        self.assertRaises(ValueError, self.app.users.get, 1)

    def test_application_users_can_be_created(self):
        user_data = {
            'first_name': 'Myfc ID',
            'last_name': 'Clients',
            'email': test_user_email,
            'password': test_user_password,
            'password2': test_user_password,
            'tos': True,
        }

        with use_pw_cassette('user/registration_success'):
            user = self.app.users.create(**user_data)

        self.assertTrue(isinstance(user, Identity))

    def test_application_users_must_be_created_with_correct_data(self):
        user_data = {
            'first_name': 'Myfc ID',
            'last_name': 'Clients',
            'email': test_user_email,
            'password': test_user_password,
            'tos': True,
        }

        with use_pw_cassette('user/registration_failure_one_password'):
            self.assertRaises(requests.HTTPError, self.app.users.create ,**user_data)

    def test_application_must_have_permissions_to_create_users(self):
        user_data = {
            'first_name': 'Myfc ID',
            'last_name': 'Clients',
            'email': test_user_email,
            'password': test_user_password,
            'password2': test_user_password,
            'tos': True,
        }

        with use_pw_cassette('user/registration_failure_app_without_permissions'):
            self.assertRaises(requests.HTTPError, self.app.users.create ,**user_data)

    def test_user_email_must_be_unique(self):
        user_data = {
            'first_name': 'Myfc ID',
            'last_name': 'Clients',
            'email': test_user_email,
            'password': test_user_password,
            'password2': test_user_password,
            'tos': True,
        }

        with use_pw_cassette('user/registration_failure_duplicated_email'):
            self.assertRaises(requests.HTTPError, self.app.users.create ,**user_data)

    def test_user_cpf_must_be_unique(self):
        user_data = {
            'first_name': 'Myfc ID',
            'last_name': 'Clients',
            'email': test_user_email,
            'password': test_user_password,
            'password2': test_user_password,
            'cpf': '11111111111',
            'tos': True,
        }

        with use_pw_cassette('user/registration_failure_duplicated_cpf'):
            self.assertRaises(requests.HTTPError, self.app.users.create ,**user_data)

    def test_user_cpf_must_be_valid(self):
        user_data = {
            'first_name': 'Myfc ID',
            'last_name': 'Clients',
            'email': test_user_email,
            'password': test_user_password,
            'password2': test_user_password,
            'cpf': '1111111111111111111',
            'tos': True,
        }

        with use_pw_cassette('user/registration_failure_invalid_cpf'):
            self.assertRaises(requests.HTTPError, self.app.users.create ,**user_data)

    def test_user_must_agree_with_tos(self):
        user_data = {
            'first_name': 'Myfc ID',
            'last_name': 'Clients',
            'email': test_user_email,
            'password': test_user_password,
            'password2': test_user_password,
        }

        with use_pw_cassette('user/registration_failure_missing_tos'):
            self.assertRaises(requests.HTTPError, self.app.users.create ,**user_data)

    def test_user_passwords_must_match(self):
        user_data = {
            'first_name': 'Myfc ID',
            'last_name': 'Clients',
            'email': test_user_email,
            'password': test_user_password,
            'password2': 'will not match',
            'tos': True,
        }

        with use_pw_cassette('user/registration_failure_password_mismatch'):
            self.assertRaises(requests.HTTPError, self.app.users.create ,**user_data)
