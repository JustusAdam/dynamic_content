from .admin_pages import OverviewPage, CategoryPage, SubcategoryPage, OverviewCommon
from .model import *
from dynct.util import typesafe
from dynct.core import model as coremodel

__author__ = 'justusadam'

name = 'admin'


def common_handler(item_type):
    handlers = {
        'menu': OverviewCommon
    }
    return handlers[item_type]


def new_category(machine_name:str, display_name, description='', weight=0):
    return Category.create(machine_name=machine_name, display_name=display_name, description=description, weight=weight)


@typesafe.typesafe
def new_subcategory(machine_name:str, display_name, category:Category, description='', weight=0):
    return Subcategory.create(machine_name=machine_name, display_name=display_name, category=category, description=description, weight=weight)


@typesafe.typesafe
def new_page(machine_name:str, display_name, subcategory:Subcategory, handler_module:coremodel.Module, description='', weight=0):
    return AdminPage.create(machine_name=machine_name, display_name=display_name, subcategory=subcategory, handler_module=handler_module, description=description, weight=weight)