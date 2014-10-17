"""
Implementation for file access and page creation. Latter may become dynamic in the future allowing pages to use their
own page handlers.
"""

from pathlib import Path
from urllib.parse import quote_plus
import mimetypes

from core.handlers.page import Page, TemplateBasedPage
from core.handlers.base import RedirectMixIn
from includes import bootstrap
from modules.comp.html_elements import ContainerElement, List
from errors.exceptions import MissingFileError, AccessDisabled


__author__ = 'justusadam'

_template_path = 'themes/default_theme/template/page.html'


class PathHandler(Page, RedirectMixIn):
    def __init__(self, url):
        super().__init__(url, None)
        self.page_type = 'file'
        self._document = ''

    @property
    def compiled(self):
        return self.parse_path()

    @property
    def encoded(self):
        return self.compiled

    def parse_path(self):
        if len(self._url.path) < 1:
            raise MissingFileError
        basedirs = bootstrap.FILE_DIRECTORIES[self._url.path[0]]
        if isinstance(basedirs, str):
            basedirs = (basedirs,)
        for basedir in basedirs:
            filepath = '/'.join([basedir] + self._url.path[1:])
            filepath = Path(filepath)

            if not filepath.exists():
                continue

            filepath = filepath.resolve()
            basedir = Path(basedir).resolve()

            if not bootstrap.ALLOW_HIDDEN_FILES and filepath.name.startswith('.'):
                raise AccessDisabled

            if basedir not in filepath.parents and basedir != filepath:
                raise AccessDisabled
            if filepath.is_dir():
                return self.serve_directory(filepath)
            else:
                return self.serve_file(filepath)

        raise MissingFileError

    def serve_directory(self, directory):
        if not bootstrap.ALLOW_INDEXING:
            raise AccessDisabled
        elif not self.url.path.trailing_slash:
            self.url.path.trailing_slash = True
            self.redirect(str(self.url))
        else:
            return DirectoryHandler(self.url, self._client, directory).encoded

    def serve_file(self, file):
        if self.url.path.trailing_slash:
            self.url.path.trailing_slash = False
            self.redirect(str(self.url))
        self.content_type, self.encoding = mimetypes.guess_type(str(file.name))
        return file.open('rb').read()


class DirectoryHandler(TemplateBasedPage):
    def __init__(self, url, client, real_dir):
        super().__init__(url, client)
        if not isinstance(real_dir, Path):
            Path(real_dir)
        self.directory = real_dir

    template_name = 'page'

    def _files(self):
        return filter(lambda a: not str(a.name).startswith('.'), self.directory.iterdir())

    def _render_file_list(self):
        return List(
            *[ContainerElement(
                str(a.name), html_type='a', additionals={'href': str(self.url.path) + quote_plus(str(a.name), )},
                classes={'file-link'}
            ) for a in self._files()
            ], classes={'directory-index'}, item_classes={'directory-content'}
        )

    def _fill_template(self):
        self._template['title'] = self.directory.name
        self._template['content'] = self._render_file_list()
        super()._fill_template()