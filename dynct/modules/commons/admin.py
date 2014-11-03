from dynct.backend.ar.base import SimpleVirtualDBTable, VirtualDatabase
from dynct.core.mvc.controller import Controller
from dynct.core.mvc.model import Model
from dynct.modules.comp.html_elements import TableElement
from .menus import MenuRenderer

__author__ = 'justusadam'


class MenuAdminController(Controller):
    def __init__(self):
        self.table = Menus(VirtualDatabase())
        super().__init__(menus=self.handle_menus)

    def handle_menus(self, url, client):
        if len(url.path) == 1:
            return self.overview()
        elif len(url.path) == 2:
            return self.a_menu(url, client)

    def overview(self):
        menus = list(self.table.rows())
        order = list(menus[0].keys())
        l = [order]
        for item in menus:
            l.append([item[a] for a in order])
        return Model('page', content=TableElement(*l), title='Menus Overview')

    def a_menu(self, url, client):
        menu = MenuRenderer(url.path[1])


class Menus(SimpleVirtualDBTable):

    def __init__(self, ar_database):
        super().__init__(ar_database, 'menus')