"""
Implementation for file access and page creation. Latter may become dynamic in the future allowing pages to use their
own page handlers.
"""

from pathlib import Path
from urllib.error import HTTPError

from framework.base_handlers import PageHandler
from includes import bootstrap
from includes import log


__author__ = 'justusadam'


# This list is probably wrong in many places
# it is supposed to map file endings to the appropriate filetype and encoding as a tuple
# syntax suffix: (type, encoding)
FILETYPES = {
    '.css': ('text/css', 'text/css'),
    '.mp3': ('audio/mp3', 'audio/mpeg'),
    '.ogg': ('audio/ogg', 'ogg/vorbis'),
    '.png': ('img/png', 'img/png'),
    '.ttf': ('font/ttf', 'font/ttf')
}


class FileHandler(PageHandler):

    def __init__(self, url, client_info):
        super().__init__(url, client_info)
        self.page_type = 'file'
        self._document = ''

    @property
    def compiled(self):
        try:
            return self.parse_path()
        except IsADirectoryError:
            log.write_warning('FileHandler', message='Attempted access to directory ' + str(self._url))
            raise HTTPError(str(self._url), 405, 'Indexing is not allowed', None, None)
        except PermissionError:
            log.write_warning('FileHandler', message='Attempted access to protected file ' + str(self._url))
            raise HTTPError(str(self._url), 403, 'Access prohibited by server config', None, None)
        except FileNotFoundError:
            log.write_error('FileHandler', message='Attempted access to non-existent file ' + str(self._url))
            raise HTTPError(str(self._url), 404, 'File does not exist', None, None)

    @property
    def encoded(self):
        return self.compiled

    def parse_path(self):
        if len(self._url.path) < 2:
            raise FileNotFoundError
        basedirs = bootstrap.FILE_DIRECTORIES[self._url.path[0]]
        if isinstance(basedirs, str):
            basedirs = (basedirs,)
        for basedir in basedirs:
            filepath = basedir + '/'.join([''] + self._url.path[1:])
            filepath = Path(filepath)

            if not filepath.exists():
                continue

            filepath = filepath.resolve()
            basedir = Path(basedir).resolve()

            if not bootstrap.ALLOW_HIDDEN_FILES and filepath.name.startswith('.'):
                raise PermissionError

            if basedir not in filepath.parents:
                raise PermissionError
            if filepath.is_dir():
                raise IsADirectoryError

            suffix = filepath.suffix
            if not suffix is None:
                if suffix in FILETYPES:
                    self.content_type, self.encoding = FILETYPES[suffix]
            return filepath.open('rb').read()
        raise FileNotFoundError