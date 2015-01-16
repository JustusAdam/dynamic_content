import json
from dyc.backend import orm
from dyc.includes import settings
from dyc.util import html

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


def _attach_theme_conf(model, default_theme=settings.DEFAULT_THEME):
    theme = model.theme if hasattr(model, 'theme') and model.theme else default_theme

    model.theme_conf = load_theme_conf(theme)


def _compile_stuff(model):
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




class Theme(orm.BaseModel):
    machine_name = orm.CharField(unique=True)
    enabled = orm.BooleanField(default=False)
    path = orm.CharField()