from modules.admin.database_operations import AdminOperations
from modules.admin.admin_pages import OverviewPage, CategoryPage, SubcategoryPage, OverviewCommon
from core import Modules

__author__ = 'justusadam'

name = 'admin'


def content_handler(url):
    if not url.tail:
        handler = OverviewPage
    elif len(url.tail) == 1:
        handler = CategoryPage
    elif len(url.tail) == 2:
        handler = SubcategoryPage
    else:
        handler_name = AdminOperations().get_page(url.tail[2])
        handler = Modules()[handler_name].admin_handler(url.tail[2])
    return handler


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

    from core.database_operations import ContentHandlers

    ContentHandlers().add_new('admin', 'admin', 'admin')