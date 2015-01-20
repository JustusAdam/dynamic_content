import json
from dyc.backend import orm
from dyc.core import mvc
from dyc.includes import settings
from dyc.util import html

__author__ = 'Justus Adam'
__version__ = '0.1'


config_file_name = 'config.json'


pagetitle = '<a href="/">dynamic_content - fast, lightweight and extensible</a>'


class InvisibleList(list):
    def __iadd__(self, other):
        self.extend(other)
        return self

    def __add__(self, other):
        a = InvisibleList(self)
        a.extend(other)
        return a

    def __str__(self):
        return ''.join(str(a) for a in self)


def get_theme(name):
    if name in ('active', 'default_theme'):
        name = 'default_theme'
    return Theme.get(machine_name=name)


def load_theme_conf(theme):
    if not isinstance(theme, Theme):
        theme = Theme.get(machine_name=theme)
    with open(theme.path + '/' + config_file_name) as file:
        conf = json.loads(file.read())
    conf['path'] = theme.path
    return conf


def attach_theme_conf(model, default_theme=settings.DEFAULT_THEME):
    if not hasattr(model, 'theme_config') or model.theme_config == None:
        theme = model.theme = model.theme if hasattr(model, 'theme') and model.theme else default_theme
        model.theme_config = load_theme_conf(theme)
        model.template_directory = model.theme_config['path'] + '/' + model.theme_config.get('template_directory', 'templates')


def compile_stuff(context):
    theme_path = '/theme/' + context.theme + '/'

    stylesheet_directory = theme_path + context.theme_config['stylesheet_directory']
    theme_stylesheets = (html.Stylesheet(stylesheet_directory + '/' + stylesheet)
        for stylesheet in context.theme_config.get('stylesheets', ()))

    if 'stylesheets' in context:
        context['stylesheets'] += theme_stylesheets
    else:
        context['stylesheets'] = InvisibleList(theme_stylesheets)

    scripts_directory = theme_path + context.theme_config['stylesheet_directory']
    theme_scripts = (
        str(html.Script(src=scripts_directory + '/' + script))
        for script in context.theme_config.get('scripts', ())
        )
    if 'scripts' in context:
        context['scripts'] += theme_scripts
    else:
        context['scripts'] = InvisibleList(theme_scripts)

    favicon = context.theme_config.get('favicon', 'favicon.icon')
    apple_icon = context.theme_config.get('apple-touch-icon', 'favicon.icon')
    theme_meta = (
        html.LinkElement(href=theme_path + favicon, rel='shortcut icon'),
        html.LinkElement(href=theme_path + apple_icon, rel='apple-touch-icon-precomposed')
    )
    if 'meta' in context:
        context['meta'] += [theme_meta]
    else:
        context['meta'] = InvisibleList(theme_meta)

    context.setdefault('pagetitle', pagetitle)


def theme_model(model_map):
    if not hasattr(model_map, 'theme_config') or not model_map.theme_config:
        attach_theme_conf(model_map)
        compile_stuff(model_map)


def theme(default_theme=settings.DEFAULT_THEME):
    @mvc.context.apply_to_context(apply_before=False)
    def _inner(model_map):
        theme_model(model_map)

    if callable(default_theme):
        func, default_theme = default_theme, settings.DEFAULT_THEME
        return _inner(func)
    elif isinstance(default_theme, str):
        return _inner
    else:
        raise TypeError('Expected {} or {}, got {}'.format(callable, str, type(default_theme)))


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
                html.ContainerElement(
                    name,
                    html_type='a',
                    classes={'breadcrumb'},
                    additional={'href': location}
                )
            ):
                yield i

    return html.ContainerElement(*tuple(acc()), classes={'breadcrumbs'})


def attach_breadcrumbs(model_map):
    if not 'breadcrumbs' in model_map:
        model_map['breadcrumbs'] = render_breadcrumbs(model_map.request.path)


@mvc.context.apply_to_context(apply_before=False)
def breadcrumbs(model_map):
    attach_breadcrumbs(model_map)


def add_theme(name, path, enabled):
    return Theme.create(
        machine_name=name,
        path=path,
        enabled=enabled
    )


class Theme(orm.BaseModel):
    machine_name = orm.CharField(unique=True)
    enabled = orm.BooleanField(default=False)
    path = orm.CharField()