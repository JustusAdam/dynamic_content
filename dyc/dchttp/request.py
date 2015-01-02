"""
Implementation of the request handler.

This class is being instantiated by the HTTP server when a request is received. This file should not be changed by
non-core developers as it *should* not need altering.
"""

import re


__author__ = 'justusadam'

_catch_errors = False

HEADER_SPLIT_REGEX = re.compile("(\S+?)\s*:\s*(\S+)")


class Request(object):
    def __init__(self, path, method, query):
        self.path = path
        self.method = method
        self.query = query
        self.client = None