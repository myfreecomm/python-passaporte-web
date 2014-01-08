# -*- coding: utf-8 -*-
import unittest

import requests
from helpers import use_cassette as use_pw_cassette

from passaporte_web.main import Application, Identity, ServiceAccount
from passaporte_web.tests.helpers import TEST_USER, APP_CREDENTIALS

__all__ = ['IdentityAccountsTest']

class IdentityAccountsTest(unittest.TestCase):

    def setUp(self):
        with use_pw_cassette('application/collections_options'):
            self.app = Application(**APP_CREDENTIALS)

        with use_pw_cassette('user/get_by_uuid'):
            self.user = self.app.users.get(uuid=TEST_USER['uuid'])

    def test_user_accounts_can_be_updated_with_same_data(self):
        service_account = self.user.accounts.from_seed().next()

        with use_pw_cassette('accounts/load_options_and_update'):
            service_account.load_options()
            updated_service_account = service_account.save()

        self.assertEquals(service_account._meta['fields'], ['plan_slug', 'expiration'])
        self.assertEquals(updated_service_account.plan_slug, service_account.plan_slug)
        self.assertEquals(updated_service_account.expiration, service_account.expiration)

    def test_user_account_format_changes_after_update(self):
        service_account = self.user.accounts.from_seed().next()

        with use_pw_cassette('accounts/load_options_and_update'):
            service_account.load_options()
            updated_service_account = service_account.save()

        self.assertEquals(
            service_account.resource_data.keys(), [
                u'plan_slug', u'name', u'roles', u'url', u'expiration',u'notifications_url',
                u'external_id', u'uuid'
        ])
        self.assertEquals(
            updated_service_account.resource_data.keys(), [
                u'history_url', u'plan_slug', u'updated_by', u'members_data', u'updated_at', u'url',
                u'expiration', u'notifications_url', u'service_data', u'account_data', u'add_member_url'
        ])

    def test_account_name_and_uuid_are_always_at_the_same_place(self):
        """
        The account name and uuid are readable using a single method,
        in spite of having multiple possible representations (and even multiple types)
        """

        with use_pw_cassette('accounts/load_options_and_update_all'):
            for item in self.user.accounts.from_seed():
                name, uuid = item.name, item.uuid

                if isinstance(item, ServiceAccount):
                    item.load_options()
                    updated_item = item.save()
                else:
                    # Accounts cannot be manipulated directly
                    continue

                self.assertEquals(name, updated_item.name)
                self.assertEquals(uuid, updated_item.uuid)
