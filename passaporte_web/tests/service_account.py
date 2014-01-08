# -*- coding: utf-8 -*-
import unittest

import requests
from api_toolkit import Collection
from helpers import use_cassette as use_pw_cassette

from passaporte_web.main import Application, Identity, ServiceAccount, Account
from passaporte_web.tests.helpers import TEST_USER, APP_CREDENTIALS

__all__ = ['IdentityAccountsTest']

class BaseServiceAccountCollectionsTest(unittest.TestCase):
    collection = None
    healty_account = 'a4c9bce4-2a8c-452f-ae13-0a0b69dfd4ba'
    expired_account = '678abf63-eb1e-433d-9f0d-f46b44ab741d'
    account_from_other_service = '1bcde52d-7da8-4800-bd59-dfea96933ce4'

    def test_get_account(self):
        with use_pw_cassette('accounts/get'):
            account = self.collection.get(self.healty_account)

        self.assertTrue(isinstance(account, ServiceAccount))

    def test_get_expired_account(self):
        with use_pw_cassette('accounts/get_expired_account'):
            account = self.collection.get(self.expired_account)

        self.assertTrue(isinstance(account, ServiceAccount))

    def test_get_account_from_other_service_fails(self):
        with use_pw_cassette('accounts/get_account_from_other_service'):
            self.assertRaises(
                requests.HTTPError, self.collection.get,
                self.account_from_other_service
            )

    def test_get_without_permissions(self):
        with use_pw_cassette('accounts/application_without_permissions'):
            self.assertRaises(
                requests.HTTPError, self.collection.get,
                self.healty_account
            )

    def test_get_using_invalid_credentials(self):
        with use_pw_cassette('accounts/using_invalid_credentials'):
            self.collection._session.auth = ('invalid', 'credentials')
            self.assertRaises(
                requests.HTTPError, self.collection.get,
                self.healty_account
            )


class IdentityAccountsTest(BaseServiceAccountCollectionsTest):

    def setUp(self):
        with use_pw_cassette('application/collections_options'):
            self.app = Application(**APP_CREDENTIALS)

        with use_pw_cassette('user/get_by_uuid'):
            self.user = self.app.users.get(uuid=TEST_USER['uuid'])

        self.collection = self.user.accounts

    def test_user_accounts_are_a_collection(self):
        self.assertTrue(isinstance(self.user.accounts, Collection))

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

    def test_load_user_accounts(self):
        with use_pw_cassette('accounts/load_user_accounts'):
            user_accounts = list(self.user.accounts.all())

        self.assertEquals(len(user_accounts), 4)
        for item in user_accounts:
            self.assertTrue(isinstance(item, ServiceAccount))

    def test_load_for_user_without_accounts(self):
        with use_pw_cassette('accounts/load_for_user_without_accounts'):
            user_accounts = list(self.user.accounts.all())

        self.assertEquals(len(user_accounts), 0)

    def test_load_for_application_without_permissions(self):
        with use_pw_cassette('accounts/application_without_permissions'):
            self.assertRaises(requests.HTTPError, self.user.accounts.all().next)

    def test_load_using_invalid_credentials(self):
        with use_pw_cassette('accounts/using_invalid_credentials'):
            self.user.accounts._session.auth = ('invalid', 'credentials')
            self.assertRaises(requests.HTTPError, self.user.accounts.all().next)

    def test_user_accounts_cannot_be_deleted(self):
        with use_pw_cassette('accounts/load_user_accounts'):
            first_account = self.user.accounts.all().next()

        with use_pw_cassette('accounts/account_options'):
            first_account.load_options()

        self.assertRaises(ValueError, first_account.delete)

    def test_load_expired_user_accounts(self):
        with use_pw_cassette('accounts/load_expired_user_accounts'):
            user_accounts = list(self.user.accounts.all(include_expired_accounts=True))

        self.assertEquals(len(user_accounts), 6)
        for item in user_accounts:
            self.assertTrue(isinstance(item, ServiceAccount))

    def test_load_user_accounts_from_other_services(self):
        with use_pw_cassette('accounts/load_user_accounts_from_other_services'):
            user_accounts = list(self.user.accounts.all(include_other_services=True))

        self.assertEquals(len(user_accounts), 5)
        for item in user_accounts[:-1]:
            self.assertTrue(isinstance(item, ServiceAccount))

        # The last item is an account from another application
        self.assertTrue(isinstance(user_accounts[-1], Account))

    def test_load_expired_user_accounts_from_other_services(self):
        with use_pw_cassette('accounts/load_expired_user_accounts_from_other_services'):
            user_accounts = list(self.user.accounts.all(
                include_expired_accounts=True,
                include_other_services=True
            ))

        self.assertEquals(len(user_accounts), 7)
        for item in user_accounts[:-1]:
            self.assertTrue(isinstance(item, ServiceAccount))

        # The last item is an account from another application
        self.assertTrue(isinstance(user_accounts[-1], Account))

    def test_load_user_accounts_with_a_given_role(self):
        with use_pw_cassette('accounts/load_user_accounts_with_a_given_role'):
            user_accounts = list(self.user.accounts.all(role='owner'))

        self.assertEquals(len(user_accounts), 2)
        for item in user_accounts:
            self.assertEquals(item.roles, ['owner'])

    def test_load_expired_user_accounts_with_a_given_role(self):
        with use_pw_cassette('accounts/load_expired_user_accounts_with_a_given_role'):
            user_accounts = list(self.user.accounts.all(
                role='owner',
                include_expired_accounts=True
            ))

        self.assertEquals(len(user_accounts), 4)
        for item in user_accounts:
            self.assertEquals(item.roles, ['owner'])

    def test_load_user_accounts_with_a_given_role_from_other_services(self):
        with use_pw_cassette('accounts/load_user_accounts_with_a_given_role_from_other_services'):
            user_accounts = list(self.user.accounts.all(
                role='owner',
                include_other_services=True
            ))

        self.assertEquals(len(user_accounts), 5)
        # The first 2 items are accounts from the authenticated application
        for item in user_accounts[:2]:
            self.assertEquals(item.roles, ['owner'])

        # The last 3 items are accounts from another application
        for item in user_accounts[2:]:
            self.assertTrue(isinstance(item, Account))

    def test_load_expired_user_accounts_with_a_given_role_from_other_services(self):
        with use_pw_cassette('accounts/load_expired_user_accounts_with_a_given_role_from_other_services'):
            user_accounts = list(self.user.accounts.all(
                role='owner',
                include_other_services=True
            ))

        self.assertEquals(len(user_accounts), 5)
        # The first 2 items are accounts from the authenticated application
        for item in user_accounts[:2]:
            self.assertEquals(item.roles, ['owner'])

        # The last 3 items are accounts from another application
        for item in user_accounts[2:]:
            self.assertTrue(isinstance(item, Account))

    def test_collection_url_is_right_after_success_getting_an_account(self):
        expected_url = self.collection.url
        self.test_get_account()
        self.assertEquals(self.collection.url, expected_url)

    def test_collection_url_is_right_after_failure_getting_an_account(self):
        expected_url = self.collection.url
        self.test_get_using_invalid_credentials()
        self.assertEquals(self.collection.url, expected_url)
