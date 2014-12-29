from . import pages, model
from dynct.util import typesafe
from dynct.core import model as coremodel

__author__ = 'justusadam'

name = 'admin'


def common_handler(item_type):
    handlers = {
        'menu': pages.OverviewCommon
    }
    return handlers[item_type]


def new_category(machine_name:str, display_name, description='', weight=0):
    return model.Category.create(machine_name=machine_name, display_name=display_name, description=description,
                                 weight=weight)


@typesafe.typesafe
def new_subcategory(machine_name:str, display_name, category:model.Category, description='', weight=0):
    return model.Subcategory.create(machine_name=machine_name, display_name=display_name, category=category,
                                    description=description, weight=weight)


@typesafe.typesafe
def new_page(machine_name:str, display_name, subcategory:model.Subcategory, handler_module:coremodel.Module,
             description='', weight=0):
    return model.AdminPage.create(machine_name=machine_name, display_name=display_name, subcategory=subcategory,
                                  handler_module=handler_module, description=description, weight=weight)