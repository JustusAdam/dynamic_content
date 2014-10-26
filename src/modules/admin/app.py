from application.config import ModuleConfig
from application.fragments import AppFragment
from core.urlparser import Parser
from core.modules import Modules
from .admin_pages import *
from .database_operations import AdminOperations

__author__ = 'justusadam'


class AdminApp(AppFragment):
    _common_handlers = {
        'menu': OverviewCommon
    }

    def __init__(self, config):
        super().__init__(config)
        self.modules = Modules()
        self.url_parser = Parser('admin', ['target', 'category', 'subcategory', 'page'])
        self.ar_conn = AdminOperations()

    def handle_request(self, request):
        if hasattr(request, 'page'):
            handler_name = AdminOperations().get_page(request.page)
            handler = self.modules[handler_name].admin_handler(request.page)
        elif hasattr(request, 'subcategory'):
            handler = SubcategoryPage
        elif hasattr(request, 'category'):
            handler = CategoryPage
        else:
            handler = OverviewPage
        return handler

    def common_handler(self, item_type):
        return self._common_handlers[item_type]

    def new_category(self, machine_name, display_name, description='', weight=0):
        self.ar_conn.add_category(machine_name, display_name, description, weight)

    def new_subcategory(self, machine_name, display_name, category, description='', weight=0):
        self.ar_conn.add_subcategory(machine_name, display_name, category, description, weight)

    def new_page(self, machine_name, display_name, subcategory, handler_module, description='', weight=0):
        self.ar_conn.add_page(machine_name, display_name, subcategory, handler_module, description, weight)

    def setup_fragment(self):
        self.ar_conn.init_tables()
        from core.database_operations import ContentHandlers

        ContentHandlers().add_new('admin', 'admin', 'admin')


class AdminAppConfig(ModuleConfig):
    pass