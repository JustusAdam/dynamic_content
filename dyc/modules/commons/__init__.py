from . import commons, menus, admin, model
from .component import register, implements
from .base import Handler
from .decorator import Regions
from dyc.core import model as coremodel


__author__ = 'Justus Adam'


def common_handler(item_type):
    handlers = {
        'menu': menus.Handler,
        'com_text': commons.TextCommons
    }
    return handlers[item_type]


def add_commons_config(machine_name, commons_type, handler_module, access_type=0):
    if isinstance(handler_module, str):
        handler_module = coremodel.Module.get(machine_name=handler_module)
    elif not isinstance(handler_module, (int, float)):
        raise ValueError
    model.CommonsConfig.create(
        machine_name=machine_name,
        element_type=commons_type,
        handler_module=handler_module,
        access_type=access_type
        )


def assign_common(common_name, region, weight, theme, render_args=None, show_title=True):
    model.Common.create(
        machine_name=common_name,
        region=region,
        weight=weight,
        theme=coremodel.Theme.get(machine_name=theme),
        render_args=render_args,
        show_title=show_title
        )
