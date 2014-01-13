# -*- coding: utf-8 -*-
import unittest

import requests
from helpers import use_cassette as use_pw_cassette

from passaporte_web.main import Application, PWebResource, PWebCollection
from passaporte_web.tests.helpers import TEST_USER, APP_CREDENTIALS

__all__ = ['AccountHistoryTest']


class AccountHistoryTest(unittest.TestCase):
    
    def setUp(self):
        with use_pw_cassette('application/collections_options'):
            self.app = Application(**APP_CREDENTIALS)

        with use_pw_cassette('user/get_by_uuid'):
            self.user = self.app.users.get(uuid=TEST_USER['uuid'])

        with use_pw_cassette('accounts/load_user_accounts'):
            self.service_account = self.user.accounts.all().next()
            self.service_account.load_options()

    def test_history_is_a_collection(self):
        self.assertTrue(isinstance(self.service_account.history, PWebCollection))

    def test_history_all_returns_a_list_of_resources(self):
        with use_pw_cassette('accounts/history'):   
            history = list(self.service_account.history.all())
    
        for i in history:
            self.assertTrue(isinstance(i, PWebResource))
            self.assertTrue(i.resource_data.has_key('solution_slug'))
            self.assertTrue(i.resource_data.has_key('created_at'))
            self.assertTrue(i.resource_data.has_key('created_by'))
            self.assertTrue(i.resource_data.has_key('expiration'))
            self.assertTrue(i.resource_data.has_key('plan_slug'))
            self.assertTrue(i.resource_data.has_key('external_id'))
       
