"""
Implementation for file and directory access.
"""

from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import quote_plus
import mimetypes
from application.fragments import AppFragment

from core.handlers.base import AbstractContentCompiler, TemplateBasedContentCompiler
from core.urlparser import Parser
from includes import bootstrap
from modules.comp.html_elements import ContainerElement, List
from errors.exceptions import MissingFileError, AccessDisabled


__author__ = 'justusadam'

_template_path = 'themes/default_theme/template/page.html'


class PathHandler(AppFragment):
    handle_request = dict([(a, handle_path ) for a in bootstrap.FILE_DIRECTORIES])
    url_parser = Parser('target')


def handle_path(url):
    basedirs = bootstrap.FILE_DIRECTORIES[url.path[0]]
    if isinstance(basedirs, str):
        basedirs = (basedirs,)
    for basedir in basedirs:
        filepath = '/'.join([basedir] + url.path[1:])
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
            return DirectoryHandler(filepath, url)
        else:
            return FileHandler(filepath, url)
    raise MissingFileError


class FileHandler(AbstractContentCompiler):
    headers = []

    def __init__(self, filepath, url):
        self.filepath = filepath
        self.url = url
        self.page_type = 'file'
        self._document = ''

    @property
    def compiled(self):
        return self.serve_file()

    @property
    def encoded(self):
        return self.compiled

    def serve_file(self):
        if self.url.path.trailing_slash:
            self.url.path.trailing_slash = False
            self.redirect(str(self.url))
        self.content_type, self.encoding = mimetypes.guess_type(str(self.filepath.name))
        return self.filepath.open('rb').read()

    def redirect(self, destination):
        raise HTTPError(str(self.url), 302, 'Redirect',
                        [('Location', destination), ('Connection', 'close')], None)


class DirectoryHandler(TemplateBasedContentCompiler):
    template_name = 'page'
    headers = []
    content_type = 'text/html'

    def __init__(self, real_dir, url):
        super().__init__()
        if not isinstance(real_dir, Path):
            Path(real_dir)
        self.directory = real_dir
        self.url = url

    def _get_template_path(self):
        return _template_path

    def _fill_template(self):
        self._template['content'] = self.serve_directory()
        super()._fill_template()

    def _files(self):
        return filter(lambda a: not str(a.name).startswith('.'), self.directory.iterdir())

    def _render_file_list(self):
        return List(
            *[ContainerElement(
                str(a.name), html_type='a', additionals={'href': str(self.url) + '/' + quote_plus(str(a.name), )},
                classes={'file-link'}
            ) for a in self._files()
            ], classes={'directory-index'}, item_classes={'directory-content'}
        )

    def serve_directory(self):
        if not bootstrap.ALLOW_INDEXING:
            raise AccessDisabled
        elif not self.url.path.trailing_slash:
            self.url.path.trailing_slash = True
            self.url(str(self.url))
        else:
            return self._render_file_list()