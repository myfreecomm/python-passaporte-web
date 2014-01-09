# -*- coding: utf-8 -*-
import os
from vcr import VCR                                                  

__all__ = ['use_cassette']

def use_cassette(*args, **kwargs):
    return VCR(
        cassette_library_dir = os.path.join(os.path.dirname(__file__), 'cassettes', 'passaporte_web'),
        match_on = ['url', 'method', 'headers', 'body'],
        record_mode = 'new_episodes',
    ).use_cassette(*args, **kwargs)


TEST_USER = {
    'email': 'identity_client@disposableinbox.com',
    'password': '*SudN7%r$MiYRa!E',
    'id_token': '729dd3a15cf03a80024d0986deee9ae91fdd5d834fabf6f9',
    'uuid': 'c3769912-baa9-4a0c-9856-395a706c7d57',
}

TEST_USER_2 = {
    'email': 'identity_client_2@disposableinbox.com',
    'uuid': 'bedcd531-c741-4d32-90d7-a7f7432f3f15',
}

APP_CREDENTIALS = {
    'host': 'http://sandbox.app.passaporteweb.com.br',
    'token': 'qxRSNcIdeA',
    'secret': '1f0AVCZPJbRndF9FNSGMOWMfH9KMUDaX',
}
