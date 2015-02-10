from framework import mvc
from framework.util import html
from . import model

__author__ = 'Justus Adam'
__version__ = '0.1'


breadcrumb_separator = '>>'


def get_breadcrumbs(url):
    path = url.split('/')
    yield 'home', '/'
    for i in range(1, len(path)):
        yield path[i], '/'.join(path[:i+1])


def render_breadcrumbs(url):
    def acc():
        for (name, location) in get_breadcrumbs(url):
            for i in (
                html.ContainerElement(
                    breadcrumb_separator,
                    html_type='span',
                    classes={'breadcrumb-separator'}
                ),
                html.A(
                    location,
                    name,
                    classes={'breadcrumb'}
                )
            ):
                yield i

    return html.ContainerElement(*tuple(acc()), classes={'breadcrumbs'})


def attach_breadcrumbs(dc_obj):
    if not 'breadcrumbs' in dc_obj:
        dc_obj.context['breadcrumbs'] = render_breadcrumbs(dc_obj.request.path)


@mvc.context.apply_to_context(apply_before=False)
def breadcrumbs(dc_obj):
    attach_breadcrumbs(dc_obj)


def add_theme(name, path, enabled):
    return model.Theme.create(
        machine_name=name,
        path=path,
        enabled=enabled
    )