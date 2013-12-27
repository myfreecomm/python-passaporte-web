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
