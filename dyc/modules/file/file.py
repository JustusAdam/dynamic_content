"""
Implementation for file access and page creation. Latter may become dynamic in the future allowing pages to use their
own page handlers.
"""

import pathlib
from urllib import parse
import mimetypes
from dyc import dchttp
from dyc import core
from dyc.core import mvc
from dyc.includes import settings
from dyc.util import html
from dyc.dchttp import response, request as _request
from dyc import middleware


__author__ = 'Justus Adam'

_template_path = 'themes/default_theme/template/page.html'

_default_view = 'indexdir'


def handle(request):
    path_split = request.path.split('/')
    # print(request.path)
    path_split = path_split[1:] if path_split[0] == '' else path_split
    trailing_slash, path_split = (True, path_split[:-1]) if path_split[-1] == '' else (False, path_split)
    if len(path_split) < 1:
        return response.Response(code=response.HttpResponseCodes.NotFound)
    basedirs = settings.FILE_DIRECTORIES[path_split[0]]
    if isinstance(basedirs, str):
        basedirs = (basedirs,)
    for basedir in basedirs:
        filepath = '/'.join([basedir] + path_split[1:])
        filepath = pathlib.Path(filepath)

        if not filepath.exists():
            continue

        filepath = filepath.resolve()
        basedir = pathlib.Path(basedir).resolve()

        if not settings.ALLOW_HIDDEN_FILES and filepath.name.startswith('.'):
            return response.Response(code=response.HttpResponseCodes.Forbidden)

        if basedir not in filepath.parents and basedir != filepath:
            return response.Response(code=response.HttpResponseCodes.Forbidden)
        if filepath.is_dir():
            if not settings.ALLOW_INDEXING:
                return response.Response(code=response.HttpResponseCodes.Forbidden)
            elif not trailing_slash:
                return response.Redirect(location='{}/'.format(request.path))
            else:
                return directory(request, filepath)
        else:
            if trailing_slash:
                return response.Redirect(location=request.path[:-1])
            return response.Response(
                body=filepath.open('rb').read(),
                headers={'Content-Type':'{};charset={}'.format(*mimetypes.guess_type(str(filepath.name)))}
                )
    return response.Response(code=response.HttpResponseCodes.NotFound)



@mvc.controller_class
class PathHandler(middleware.Handler):
    @mvc.controller_method({'theme/**', 'public/**', '/**'}, method=dchttp.RequestMethods.GET)
    def handle(self, model, path):
        return self.parse_path(model, path)

    def parse_path(self, model, path):
        # HACK until all handler methods use the requests properly, this method creates its own
        return handle(_request.Request(path, 'get', None, None))

    def handle_request(self, request):
        if request.path.split('/')[1] in settings.FILE_DIRECTORIES:
            return handle(request)
        return None


def directory(request, real_dir):
    if not isinstance(real_dir, pathlib.Path):
        real_dir = pathlib.Path(real_dir)
    model = mvc.context.Context(
        content=html.List(
            *[html.ContainerElement(
                str(a.name), html_type='a', additional={'href': str(request.path) + parse.quote(str(a.name), )},
                classes={'file-link'}
            ) for a in filter(lambda a: not str(a.name).startswith('.'), real_dir.iterdir())
            ], classes={'directory-index'}, item_classes={'directory-content'}
        ),
        title=real_dir.name
    )
    return core.get_component('TemplateFormatter')(_default_view, model, request)
