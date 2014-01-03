# -*- coding: utf-8 -*-
import unittest

import requests
import api_toolkit
from helpers import use_cassette as use_pw_cassette

from passaporte_web.main import Application, Identity, Profile, ServiceAccount
from passaporte_web.tests.helpers import TEST_USER, APP_CREDENTIALS

__all__ = ['IdentityTest', 'IdentityAccountsTest']

class IdentityTest(unittest.TestCase):

    def setUp(self):
        with use_pw_cassette('application/collections_options'):
            self.app = Application(**APP_CREDENTIALS)

        with use_pw_cassette('user/get_by_uuid'):
            self.user = self.app.users.get(uuid=TEST_USER['uuid'])

    def test_user_has_profile(self):
        with use_pw_cassette('profile/read'):
            profile = self.user.profile

        self.assertTrue(isinstance(profile, Profile))

    def test_user_profile_can_be_updated_with_same_data(self):
        with use_pw_cassette('profile/read'):
            profile = self.user.profile

        with use_pw_cassette('profile/update_with_same_data'):
            profile = profile.save()

        self.assertTrue(isinstance(profile, Profile))

    def test_user_profile_can_be_updated(self):
        with use_pw_cassette('profile/read'):
            profile = self.user.profile

        profile.bio = u'Um usuário usado em testes'
        profile.nickname = u'teste-user'

        with use_pw_cassette('profile/update'):
            updated_profile = profile.save()

        self.assertTrue(isinstance(updated_profile, Profile))
        self.assertEquals(updated_profile.bio, profile.bio)
        self.assertEquals(updated_profile.nickname, profile.nickname)

    def test_application_must_have_permission_to_update_user_profile(self):
        with use_pw_cassette('profile/read'):
            profile = self.user.profile

        with use_pw_cassette('profile/update_without_permissions'):
            self.assertRaises(requests.HTTPError, profile.save)

    def test_user_info_can_be_updated_with_same_data(self):
        with use_pw_cassette('user/update_with_same_data'):
            user = self.user.save()

        self.assertTrue(isinstance(user, Identity))

    def test_user_info_can_be_updated(self):
        self.user.send_partner_news = False
        self.user.send_myfreecomm_news = False

        with use_pw_cassette('user/update'):
            updated_user = self.user.save()

        self.assertTrue(isinstance(updated_user, Identity))
        self.assertEquals(updated_user.send_partner_news, False)
        self.assertEquals(updated_user.send_myfreecomm_news, False)

    def test_user_cpf_must_be_valid(self):
        # cpf cannot be updated by default
        self.user._meta['fields'].append('cpf') 
        self.user.resource_data['cpf'] = '11111111110'

        with use_pw_cassette('user/update_with_invalid_cpf'):
            self.assertRaises(requests.HTTPError, self.user.save)

    def test_user_cpf_is_unique(self):
        # cpf cannot be updated by default
        self.user._meta['fields'].append('cpf') 
        self.user.resource_data['cpf'] = '11111111111'

        with use_pw_cassette('user/update_with_duplicated_cpf'):
            self.assertRaises(requests.HTTPError, self.user.save)

    def test_application_must_have_permission_to_update_user_info(self):
        with use_pw_cassette('user/update_without_permissions'):
            self.assertRaises(requests.HTTPError, self.user.save)


class IdentityAccountsTest(unittest.TestCase):

    def setUp(self):
        with use_pw_cassette('application/collections_options'):
            self.app = Application(**APP_CREDENTIALS)

        with use_pw_cassette('user/get_by_uuid'):
            self.user = self.app.users.get(uuid=TEST_USER['uuid'])

    def test_user_accounts_can_be_updated_with_same_data(self):
        service_account = self.user.accounts[0]

        with use_pw_cassette('accounts/load_options_and_update'):
            service_account.load_options()
            updated_service_account = service_account.save()

        self.assertEquals(service_account._meta['fields'], ['plan_slug', 'expiration'])
        self.assertEquals(updated_service_account.plan_slug, service_account.plan_slug)
        self.assertEquals(updated_service_account.expiration, service_account.expiration)

    def test_user_account_format_changes_after_update(self):
        service_account = self.user.accounts[0]

        with use_pw_cassette('accounts/load_options_and_update'):
            service_account.load_options()
            updated_service_account = service_account.save()

        self.assertEquals(
            service_account.resource_data.keys(), [
                u'plan_slug', u'name', u'roles', u'url', u'notifications', u'expiration',
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
            for item in self.user.accounts:
                name, uuid = item.name, item.uuid

                if isinstance(item, ServiceAccount):
                    item.load_options()
                    updated_item = item.save()
                else:
                    # Accounts cannot be manipulated directly
                    continue

                self.assertEquals(name, updated_item.name)
                self.assertEquals(uuid, updated_item.uuid)
