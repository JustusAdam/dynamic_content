from http import cookies
from pathlib import Path
import sys
from urllib.error import HTTPError
from core.request import Request

from modules.comp.template import Template
from util.config import read_config
from modules.comp.page import Component

from errors.exceptions import InvalidInputError


__author__ = 'justusadam'


class AbstractContentCompiler:
    encoding = 'utf-8'

    @property
    def compiled(self):
        return ''

    def __str__(self):
        return str(self.compiled)

    @property
    def encoded(self):
        return str(self.compiled).encode(self.encoding)


class ContentCompiler(AbstractContentCompiler):
    _request = None
    _input_accepted = True

    def __init__(self, request):
        super().__init__()
        self.request = request
        self._headers = set()
        self._cookies = None

    @property
    def request(self):
        return self._request

    @request.setter
    def request(self, val):
        if not isinstance(val, Request):
            raise InvalidInputError
        else:
            self._request = val

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

    def _has_active_query(self):
        pass

    def _check_queries(self):
        """
        Simple routine that calls the appropriate 'process' methods IF they're necessary
        :return:
        """
        if not self._input_accepted:
            raise InvalidInputError
        if self._has_active_query():
            self._process_query()

    def _process_query(self):
        """
        This method gets called if there is a valid post query present.

        :return:
        """
        pass


class RedirectMixIn(ContentCompiler):
    def redirect(self, destination=None):
        if 'destination' in self.request.get_query:
            destination = self.request.get_query['destination'][0]
        elif not destination:
            destination = str(self.request.path.prt_to_str(0, -1))
        raise HTTPError(str(self.request), 302, 'Redirect',
                        [('Location', destination), ('Connection', 'close')], None)


class TemplateBasedContentCompiler(AbstractContentCompiler):
    _theme = 'default_theme'

    template_name = ''

    def __init__(self):
        super().__init__()
        self.theme_config = read_config(self.theme_path + '/config.json')
        self._template = Template(self._get_template_path())

    @property
    def theme(self):
        return self._theme

    @property
    def theme_path(self):
        return 'themes/' + self.theme

    @property
    def theme_path_alias(self):
        return '/theme/' + self.theme

    @property
    def compiled(self):
        # TODO add callback function instead of rendering page directly
        self._fill_template()
        page = Component(self._template)
        return page

    def _get_template_path(self):
        path = self.theme_path
        if 'template_directory' in self.theme_config:
            path += '/' + self.theme_config['template_directory']
        else:
            path += '/' + 'templates'
        return path + '/' + self.template_name + '.html'

    def _get_my_folder(self):
        return str(Path(sys.modules[self.__class__.__module__].__file__).parent)

    def _get_config_folder(self):
        return self._get_my_folder()

    def _fill_template(self):
        pass