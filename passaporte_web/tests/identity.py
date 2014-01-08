# -*- coding: utf-8 -*-
import unittest

import requests
from helpers import use_cassette as use_pw_cassette

from passaporte_web.main import Application, Identity, Profile
from passaporte_web.tests.helpers import TEST_USER, APP_CREDENTIALS

__all__ = ['IdentityTest']

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

