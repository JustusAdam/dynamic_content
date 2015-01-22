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


def attach_theme_conf(dc_obj, default_theme=settings.DEFAULT_THEME):
    if not 'theme_config' in dc_obj.config or dc_obj.config['theme_config'] is None:
        theme = dc_obj.config['theme'] = dc_obj.config['theme'] if 'theme' in dc_obj.config and dc_obj.config['theme'] else default_theme
        dc_obj.config['theme_config'] = load_theme_conf(theme)
        dc_obj.config['template_directory'] = dc_obj.config['theme_config']['path'] + '/' + dc_obj.config['theme_config'].get('template_directory', 'templates')


def compile_stuff(dc_obj):
    theme_path = '/theme/' + dc_obj.config['theme'] + '/'

    stylesheet_directory = theme_path + dc_obj.config['theme_config']['stylesheet_directory']
    theme_stylesheets = (html.Stylesheet(stylesheet_directory + '/' + stylesheet)
        for stylesheet in dc_obj.config['theme_config'].get('stylesheets', ()))

    if 'stylesheets' in dc_obj.context:
        dc_obj.context['stylesheets'] += theme_stylesheets
    else:
        dc_obj.context['stylesheets'] = InvisibleList(theme_stylesheets)

    scripts_directory = theme_path + dc_obj.config['theme_config']['stylesheet_directory']
    theme_scripts = (
        str(html.Script(src=scripts_directory + '/' + script))
        for script in dc_obj.config['theme_config'].get('scripts', ())
        )
    if 'scripts' in dc_obj.context:
        dc_obj.context['scripts'] += theme_scripts
    else:
        dc_obj.context['scripts'] = InvisibleList(theme_scripts)

    favicon = dc_obj.config['theme_config'].get('favicon', 'favicon.icon')
    apple_icon = dc_obj.config['theme_config'].get('apple-touch-icon', 'favicon.icon')
    theme_meta = (
        html.LinkElement(href=theme_path + favicon, rel='shortcut icon'),
        html.LinkElement(href=theme_path + apple_icon, rel='apple-touch-icon-precomposed')
    )
    if 'meta' in dc_obj.context:
        dc_obj.context['meta'] += [theme_meta]
    else:
        dc_obj.context['meta'] = InvisibleList(theme_meta)

    dc_obj.context.setdefault('pagetitle', pagetitle)


def theme_dc_obj(dc_obj):
    if not 'theme_config' in dc_obj.config or not dc_obj.config['theme_config']:
        attach_theme_conf(dc_obj)
        compile_stuff(dc_obj)


def theme(default_theme=settings.DEFAULT_THEME):
    @mvc.context.apply_to_context(apply_before=False)
    def _inner(dc_obj):
        theme_dc_obj(dc_obj)

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


def attach_breadcrumbs(dc_obj):
    if not 'breadcrumbs' in dc_obj:
        dc_obj.context['breadcrumbs'] = render_breadcrumbs(dc_obj.request.path)


@mvc.context.apply_to_context(apply_before=False)
def breadcrumbs(dc_obj):
    attach_breadcrumbs(dc_obj)


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
