from application.app import AppFragment
from modules.comp import database_operations as dbo

__author__ = 'justusadam'


class DecoratorApp(AppFragment):
    def __init__(self, config):
        super().__init__(config)
        self.dbo = dbo.RegionOperations()

    def add_commons_config(self, machine_name, commons_type, handler_module, show_title=True, access_type=0):
        self.dbo.add_item_conf(machine_name, commons_type, handler_module, show_title, access_type)


    def assign_common(self, common_name, region, weight, theme):
        self.dbo.add_item(common_name, region, weight, theme)

    def setup_fragment(self):
        ro = dbo.RegionOperations()
        ro.init_tables()
        ro.add_item_conf('start_menu', 'menu', 'commons', False, 0)
        ro.add_item('start_menu', 'navigation', 1, 'default_theme')
        ro.add_item('copyright', 'footer', 1, 'default_theme')
        ro.add_item_conf('copyright', 'com_text', 'commons', False, 0)