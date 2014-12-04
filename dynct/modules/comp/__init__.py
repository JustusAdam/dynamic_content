from .model import Common
from dynct.modules.commons.model import CommonsConfig
from dynct.core.model import Module

__author__ = 'justusadam'

name = 'theme_engine'

role = 'theme_engine'


def add_commons_config(machine_name, commons_type, handler_module, access_type=0):
    if isinstance(handler_module, str):
        handler_module = Module.get(machine_name=handler_module)
    elif not isinstance(handler_module, (int, float)):
        raise ValueError
    CommonsConfig.create(machine_name=machine_name,
                         element_type=commons_type,
                         handler_module=handler_module,
                         access_type=access_type)


def assign_common(common_name, region, weight, theme, render_args=None, show_title=True):
    Common.create(name=common_name,
                  region=region,
                  weight=weight,
                  theme=theme,
                  render_args=render_args,
                  show_title=show_title)