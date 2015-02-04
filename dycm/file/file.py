"""
Implementation for file access and page creation. Latter may become dynamic in the future allowing pages to use their
own page handlers.
"""

import pathlib
from urllib import parse
import mimetypes
from dycc import http
import dycc
from dycc import route
from dycc.includes import settings
from dycc.util import html, structures
from dycc.http import response
from dycc import middleware


__author__ = 'Justus Adam'

_template_path = 'themes/default_theme/template/page.html'

_default_view = 'indexdir'


def get_file_directories():
    return settings.get('file_directories', ())


def handle(request):
    path_split = request.path.split('/')
    path_split = path_split[1:] if path_split[0] == '' else path_split
    if len(path_split) < 1:
        return response.Response(code=response.HttpResponseCodes.NotFound)
    basedirs = get_file_directories()[path_split[0]]
    if isinstance(basedirs, str):
        basedirs = (basedirs,)
    filepath = '/'.join(path_split[1:])
    basedirs = tuple(
        (settings['dc_basedir'] + '/' + bd if not bd.startswith('/') else bd)
        for bd in basedirs)
    for resp in (serve_from(request, filepath, basedir) for basedir in basedirs):
        if not resp is None:
            return resp

    return response.Response(code=response.HttpResponseCodes.NotFound)


def serve_from(request, file, basedir):

    trailing_slash = file.endswith('/')

    filepath = pathlib.Path(basedir) / file

    if not filepath.exists():
        return None

    filepath = filepath.resolve()
    basedir = pathlib.Path(basedir).resolve()

    if not settings.get('allow_hidden_files', False) and filepath.name.startswith('.'):
        return response.Response(code=response.HttpResponseCodes.Forbidden)

    if basedir not in filepath.parents and basedir != filepath:
        return response.Response(code=response.HttpResponseCodes.Forbidden)
    if filepath.is_dir():
        if not settings.get('allow_indexing', False):
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


@route.controller_class
class PathHandler(middleware.Handler):
    @route.controller_method({'theme/**', 'public/**', '/**'}, method=http.RequestMethods.GET)
    def handle(self, dc_obj, path):
        return self.parse_path(dc_obj, path)

    @staticmethod
    def parse_path(dc_obj, path):
        # HACK until all handler methods use the requests properly, this method creates its own
        return handle(dc_obj.request)

    def handle_request(self, request):
        if request.path.split('/')[1] in get_file_directories():
            return handle(request)
        return None


def directory(request, real_dir):
    if not isinstance(real_dir, pathlib.Path):
        real_dir = pathlib.Path(real_dir)
    dc_obj = structures.DynamicContent(
        request=request,
        handler_options={},
        config={},
        context=dict(
            content=html.List(
                *[html.ContainerElement(
                    str(a.name), html_type='a', additional={'href': str(request.path) + parse.quote(str(a.name), )},
                    classes={'file-link'}
                ) for a in filter(lambda a: not str(a.name).startswith('.'), real_dir.iterdir())
                ], classes={'directory-index'}, item_classes={'directory-content'}
            ),
            title=real_dir.name
            )
        )
    return dycc.get_component('TemplateFormatter')(_default_view, dc_obj)
