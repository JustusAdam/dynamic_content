from http import cookies
from pathlib import Path
import sys
from urllib.error import HTTPError

from core.mvc.model import Model
from util.config import read_config
from modules.comp.page import Component
from util.url import Url


__author__ = 'justusadam'


class ContentCompiler:
    @property
    def compiled(self):
        return ''

    def __str__(self):
        return str(self.compiled)


class WebObject(ContentCompiler):
    _url = None

    def __init__(self, url):
        super().__init__()
        self.url = url
        self._headers = set()
        self._cookies = None

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, val):
        if not isinstance(val, Url):
            self._url = Url(val)
        else:
            self._url = val

    @property
    def client(self):
        return None

    def add_header(self, key, value):
        assert isinstance(key, str)
        assert isinstance(value, str)
        self._headers.add((key, value))

    def add_morsels(self, cookie):
        if not self._cookies:
            self._cookies = cookies.SimpleCookie()
        assert isinstance(cookie, (str, dict))
        self._cookies.load(cookie)

    @property
    def cookies(self):
        if not self._cookies:
            self._cookies = cookies.SimpleCookie()
        return self._cookies

    @property
    def headers(self):
        if self._cookies:
            # since rendering cookie values with the cookie object returns a string we split it again
            # to get header and value
            name, value = self._cookies.output().split(':', 1)
            # and remove redundant space at the beginning of the value string
            value = value[1:]
            self.add_header(name, value)
        return self._headers

    def is_get(self):
        return bool(self.url.get_query)

    def is_post(self):
        return bool(self.url.post)

    def _process_queries(self):
        """
        Simple routine that calls the appropriate 'process' methods IF they're necessary
        :return:
        """
        if self.is_get():
            self._process_get()
        if self.is_post():
            self._process_post()

    def _process_get(self):
        """
        This method gets called by the class IF there are get query variables present.

        Inheriting classes should overwrite this method rather than 'process_queries'.
        :return:
        """
        pass

    def _process_post(self):
        """
        This method gets called if there is a valid post query present.

        Inheriting classes should overwrite this method rather than 'process_queries'.
        :return:
        """
        pass


class RedirectMixIn(WebObject):
    def redirect(self, destination=None):
        if 'destination' in self.url.get_query:
            destination = self.url.get_query['destination'][0]
        elif not destination:
            destination = str(self.url.path.prt_to_str(0, -1))
        raise HTTPError(str(self.url), 302, 'Redirect',
                        [('Location', destination), ('Connection', 'close')], None)


class ModelBasedContentCompiler(ContentCompiler):
    _theme = 'default_theme'

    view_name = ''

    def __init__(self):
        super().__init__()
        self._model = Model(self.view_name)
        self._model.theme = self.theme

    @property
    def theme(self):
        return self._theme

    @property
    def compiled(self):
        self._fill_model()
        return self._model

    def _fill_model(self):
        pass