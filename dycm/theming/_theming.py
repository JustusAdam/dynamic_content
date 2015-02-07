import json
import pathlib
from dycc import mvc
from dycc.includes import settings
from dycc.util import html, structures
from . import model

__author__ = 'Justus Adam'
__version__ = '0.1'


config_file_name = 'config.json'

pagetitle = '<a href="/">dynamic_content - fast, lightweight and extensible</a>'


def _default_theme():
    return settings.get('default_theme', 'default_theme')


def _default_admin_theme():
    return settings.get('default_theme', 'admin_theme')


def get_theme(name):
    if name in ('active', 'default_theme'):
        name = _default_theme()
    return model.Theme.get(machine_name=name)


def load_theme_conf(theme):
    if not isinstance(theme, model.Theme):
        theme = model.Theme.get(machine_name=theme)
    with open(str(pathlib.Path(theme.path) / config_file_name)) as file:
        conf = json.loads(file.read())
    conf['path'] = theme.path
    return conf


def attach_theme_conf(dc_obj, default_theme=None):
    default_theme = default_theme if not default_theme is None else _default_theme()
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
        dc_obj.context['stylesheets'] = structures.InvisibleList(theme_stylesheets)

    scripts_directory = theme_path + dc_obj.config['theme_config']['stylesheet_directory']
    theme_scripts = (
        str(html.Script(src=scripts_directory + '/' + script))
        for script in dc_obj.config['theme_config'].get('scripts', ())
        )
    if 'scripts' in dc_obj.context:
        dc_obj.context['scripts'] += theme_scripts
    else:
        dc_obj.context['scripts'] = structures.InvisibleList(theme_scripts)

    favicon = dc_obj.config['theme_config'].get('favicon', 'favicon.icon')
    apple_icon = dc_obj.config['theme_config'].get('apple-touch-icon', 'favicon.icon')
    theme_meta = (
        html.LinkElement(href=theme_path + favicon, rel='shortcut icon'),
        html.LinkElement(href=theme_path + apple_icon, rel='apple-touch-icon-precomposed')
    )
    if 'meta' in dc_obj.context:
        dc_obj.context['meta'] += [theme_meta]
    else:
        dc_obj.context['meta'] = structures.InvisibleList(theme_meta)

    dc_obj.context.setdefault('pagetitle', pagetitle)


def theme_dc_obj(dc_obj, default_theme=_default_theme()):
    if not 'theme_config' in dc_obj.config or not dc_obj.config['theme_config']:
        if not 'theme' in dc_obj.config:
            dc_obj.config['theme'] = default_theme
        attach_theme_conf(dc_obj)
        compile_stuff(dc_obj)


def theme(default_theme=_default_theme()):
    @mvc.context.apply_to_context(apply_before=False)
    def _inner(dc_obj):
        theme_dc_obj(dc_obj, default_theme)

    if callable(default_theme):
        func, default_theme = default_theme, _default_theme()
        return _inner(func)
    elif isinstance(default_theme, str):
        return _inner
    else:
        raise TypeError('Expected {} or {}, got {}'.format(callable, str, type(default_theme)))