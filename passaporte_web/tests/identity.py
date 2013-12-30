# -*- coding: utf-8 -*-
import unittest

import requests
import api_toolkit
from helpers import use_cassette as use_pw_cassette

from passaporte_web.main import Account, Identity

__all__ = ['IdentityTest',]

TEST_USER = {
    'email': 'identity_client@disposableinbox.com',
    'password': '*SudN7%r$MiYRa!E',
    'id_token': '729dd3a15cf03a80024d0986deee9ae91fdd5d834fabf6f9',
    'uuid': 'c3769912-baa9-4a0c-9856-395a706c7d57',
}

class IdentityTest(unittest.TestCase):

    def setUp(self):
        with use_pw_cassette('application/collections_options'):
            self.app = Application(**APP_CREDENTIALS)
