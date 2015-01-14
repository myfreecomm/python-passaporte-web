# -*- coding: utf-8 -*-
import six
import unittest

import requests
from .helpers import use_cassette as use_pw_cassette

from passaporte_web.main import PassaporteWeb, PWebResource, PWebCollection
from passaporte_web.tests.helpers import TEST_USER, APP_CREDENTIALS

__all__ = ['AccountHistoryTest']


class AccountHistoryTest(unittest.TestCase):

    def setUp(self):
        with use_pw_cassette('application/collections_options'):
            self.app = PassaporteWeb(**APP_CREDENTIALS)

        with use_pw_cassette('user/get_by_uuid'):
            self.user = self.app.users.get(uuid=TEST_USER['uuid'])

        with use_pw_cassette('accounts/load_user_accounts'):
            self.service_account = six.next(self.user.accounts.all())
            self.service_account.load_options()

    def test_history_is_a_collection(self):
        self.assertTrue(isinstance(self.service_account.history, PWebCollection))

    def test_history_all_returns_a_list_of_resources(self):
        with use_pw_cassette('accounts/history'):
            history = list(self.service_account.history.all())

        for i in history:
            self.assertTrue(isinstance(i, PWebResource))
            self.assertTrue('solution_slug' in i.resource_data)
            self.assertTrue('created_at' in i.resource_data)
            self.assertTrue('created_by' in i.resource_data)
            self.assertTrue('expiration' in i.resource_data)
            self.assertTrue('plan_slug' in i.resource_data)
            self.assertTrue('external_id' in i.resource_data)

