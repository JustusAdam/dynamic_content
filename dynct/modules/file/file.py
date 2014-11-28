"""
Implementation for file access and page creation. Latter may become dynamic in the future allowing pages to use their
own page handlers.
"""

from pathlib import Path
from urllib.parse import quote_plus
import mimetypes

from dynct.core.mvc.decorator import controller_class, controller_method
from dynct.includes import settings
from dynct.modules.comp.html_elements import ContainerElement, List


__author__ = 'justusadam'

_template_path = 'themes/default_theme/template/page.html'


@controller_class
class PathHandler:
    @controller_method('theme', get=False, post=False)
    @controller_method('public', get=False, post=False)
    def handle(self, model, url, *args):
        return self.parse_path(model, url)

    def parse_path(self, model, url):
        if len(url.path) < 1:
            raise FileNotFoundError
        basedirs = settings.FILE_DIRECTORIES[url.path[0]]
        if isinstance(basedirs, str):
            basedirs = (basedirs,)
        for basedir in basedirs:
            filepath = '/'.join([basedir] + url.path[1:])
            filepath = Path(filepath)

            if not filepath.exists():
                continue

            filepath = filepath.resolve()
            basedir = Path(basedir).resolve()

            if not settings.ALLOW_HIDDEN_FILES and filepath.name.startswith('.'):
                raise PermissionError

            if basedir not in filepath.parents and basedir != filepath:
                raise PermissionError
            if filepath.is_dir():
                if not settings.ALLOW_INDEXING:
                    raise PermissionError
                elif not url.path.trailing_slash:
                    url.path.trailing_slash = True
                    return ':redirect:' + str(url)
                else:
                    return directory(model, url, filepath)
            else:
                if url.path.trailing_slash:
                    url.path.trailing_slash = False
                    return ':redirect:' + str(url)
                model['content'] = filepath.open('rb').read()
                model.decorator_attributes.add('no-encode')
                model.content_type, model.encoding = mimetypes.guess_type(str(filepath.name))
                return ':no-view:'

        raise FileNotFoundError


def directory(model, url, real_dir):
    if not isinstance(real_dir, Path):
        real_dir = Path(real_dir)
    model['content'] = List(
            *[ContainerElement(
                str(a.name), html_type='a', additional={'href': str(url.path) + quote_plus(str(a.name), )},
                classes={'file-link'}
            ) for a in filter(lambda a: not str(a.name).startswith('.'), real_dir.iterdir())
            ], classes={'directory-index'}, item_classes={'directory-content'}
        )
    model['title'] = real_dir.name
    return 'page'