import json
from dyc.backend import orm
from dyc.includes import settings
from dyc.util import html, decorators
from dyc.core.mvc import model

__author__ = 'Justus Adam'
__version__ = '0.1'


config_file_name = 'config.json'


def load_theme_conf(theme):
    if not isinstance(theme, Theme):
        theme = Theme.get(machine_name=theme)
    with open(theme.path + config_file_name) as file:
        conf = json.load(file.read())
        conf['path'] = theme.path
        return conf


def attach_theme_conf(model, default_theme=settings.DEFAULT_THEME):
    theme = model.theme if hasattr(model, 'theme') and model.theme else default_theme

    model.theme_config = load_theme_conf(theme)


def compile_stuff(model):
    theme_path = model.theme_config.path

    stylesheet_directory = theme_path + '/' + model.theme_config['stylesheet_directory']
    model['stylesheets'] = ''.join(
        str(html.Stylesheet(stylesheet_directory + '/' + stylesheet))
        for stylesheet in model.theme_config['stylesheets']
        ) if model.theme_config['stylesheets'] else ''

    scripts_directory = theme_path + '/' + model.theme_config['stylesheet_directory']
    model['scripts'] = ''.join(
        str(html.Script(src=scripts_directory + '/' + script))
        for script in model.theme_config['scripts']
        ) if model.theme_config['scripts'] else ''

    favicon = (model.theme_config['favicon']
            if 'favicon' in model.theme_config
            else 'favicon.icon')
    model['meta'] = html.LinkElement(href=theme_path + favicon, rel='shortcut icon')


def theme(default_theme=settings.DEFAULT_THEME):
    @decorators.apply_to_type(model.Model, return_from_decorator=True)
    def _theme_decorator(func):
        def _inner(model_map):
            if not hasattr(model_map, 'theme_config') or not model_map.theme_config:
                attach_theme_conf(model_map)
                res = func()
                compile_stuff(model_map)
                return res
            else:
                return func()
        return _inner

    if callable(default_theme):
        func, default_theme = default_theme, settings.DEFAULT_THEME
        return _theme_decorator(func)
    elif isinstance(default_theme, str):
        return _theme_decorator
    else:
        raise TypeError('Expected {} or {}, got {}'.format(callable, str, type(default_theme)))


breadcrumb_separator = '>>'


def get_breadcrumbs(url):
    path = url.path.split('/')
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
                html.ContainerElement(
                    name,
                    html_type='a',
                    classes={'breadcrumb'},
                    additional={'href': location}
                )
            ):
                yield i

    return html.ContainerElement(*tuple(acc()), classes={'breadcrumbs'})


@decorators.apply_to_type(model.Model)
def breadcrumbs(model_map):
    if not 'breadcrumbs' in model_map:
        model_map['breadcrumbs'] = render_breadcrumbs(model_map.request.path)



class Theme(orm.BaseModel):
    machine_name = orm.CharField(unique=True)
    enabled = orm.BooleanField(default=False)
    path = orm.CharField()