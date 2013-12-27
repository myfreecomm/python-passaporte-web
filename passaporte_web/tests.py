# -*- coding: utf-8 -*-
from os import path
import unittest
from vcr import VCR

from passaporte_web.main import Application


class ApplicationTest(unittest.TestCase):

    def test_instance_creation(self):
        app = Application()
        import pdb; pdb.set_trace()
