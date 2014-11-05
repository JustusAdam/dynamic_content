from dynct.backend.ar.base import ARObject
from dynct.core.mvc.controller import Controller
from dynct.core.mvc.model import Model
from dynct.modules.comp.html_elements import TableElement, List, A
from dynct.modules.i18n import get_display_name
from dynct.modules.form.secure import SecureForm
from dynct.modules.comp.html_elements import Checkbox
from .menus import MenuRenderer

__author__ = 'justusadam'


class MenuAdminController(Controller):
    def __init__(self):
        super().__init__(menus=self.handle_menus)

    def handle_menus(self, url, client):
        if len(url.path) == 1:
            return self.overview(url)
        elif len(url.path) == 2:
            return self.a_menu(url, client)

    def overview(self, url):
        menus = Menus.get_all()
        l = []
        for item in menus:
            l.append(
                [
                    A(str(url.path) + '/' + item.machine_name, item.id),
                    A(str(url.path) + '/' + item.machine_name, get_display_name(item.machine_name, 'menus', 'english')),
                    Checkbox(checked=bool(item.enabled))
                ]
            )
        return Model('page', content=SecureForm(TableElement(*l, classes={'menu-overview'})), title='Menus Overview')

    def a_menu(self, url, client):
        menu_name = url.path[1]
        menu = MenuRenderer(menu_name).menu().render()
        return Model('page', content=List(*menu, additionals={'style': 'list-style-type: none;'}),
                     title=get_display_name(menu_name, 'menus', 'english'))


class Menus(ARObject):
    _table = 'menus'

    def __init__(self, id, machine_name, enabled):
        super().__init__()
        self.id = id
        self.machine_name = machine_name
        self.enabled = enabled