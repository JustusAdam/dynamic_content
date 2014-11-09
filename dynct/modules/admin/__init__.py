from .admin_pages import OverviewPage, CategoryPage, SubcategoryPage, OverviewCommon
from .admin_pages import AdminController
from .ar import *

__author__ = 'justusadam'

name = 'admin'


def common_handler(item_type):
    handlers = {
        'menu': OverviewCommon
    }
    return handlers[item_type]


def new_category(machine_name, display_name, description='', weight=0):
    Category(machine_name, display_name, description, weight).save()



def new_subcategory(machine_name, display_name, category, description='', weight=0):
    Subcategory(machine_name, display_name, category, description, weight).save()


def new_page(machine_name, display_name, subcategory, handler_module, description='', weight=0):
    AdminPage(machine_name, display_name, subcategory, handler_module, description, weight).save()


def prepare():
    from dynct.core.ar import ContentHandler

    ContentHandler('admin', 'admin', 'admin').save()