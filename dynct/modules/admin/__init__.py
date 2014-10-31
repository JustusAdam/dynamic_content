from .database_operations import AdminOperations
from .admin_pages import OverviewPage, CategoryPage, SubcategoryPage, OverviewCommon
from .admin_pages import AdminController

__author__ = 'justusadam'

name = 'admin'


def common_handler(item_type):
    handlers = {
        'menu': OverviewCommon
    }
    return handlers[item_type]


def new_category(machine_name, display_name, description='', weight=0):
    AdminOperations().add_category(machine_name, display_name, description, weight)


def new_subcategory(machine_name, display_name, category, description='', weight=0):
    AdminOperations().add_subcategory(machine_name, display_name, category, description, weight)


def new_page(machine_name, display_name, subcategory, handler_module, description='', weight=0):
    AdminOperations().add_page(machine_name, display_name, subcategory, handler_module, description, weight)


def prepare():
    ops = AdminOperations()

    ops.init_tables()

    from dynct.core.database_operations import ContentHandlers

    ContentHandlers().add_new('admin', 'admin', 'admin')