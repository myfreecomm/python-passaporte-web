# -*- coding: utf-8 -*-
import unittest

import requests
import api_toolkit
from helpers import use_cassette as use_pw_cassette

from passaporte_web.main import Application, Identity, Profile
from passaporte_web.tests.helpers import TEST_USER, APP_CREDENTIALS

__all__ = ['IdentityTest',]

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

    def test_user_profile_can_be_updated(self):
        with use_pw_cassette('profile/read'):
            profile = self.user.profile

        with use_pw_cassette('profile/update_with_same_data'):
            profile = profile.save()

        self.assertTrue(isinstance(profile, Profile))
