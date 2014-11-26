from dynct.backend.ar.base import ARObject
from dynct.core.mvc.decorator import controller_class, controller_method
from dynct.modules.comp.decorator import Regions
from dynct.modules.comp.html_elements import TableElement, List, A
from dynct.modules.i18n import get_display_name
from dynct.modules.form.secure import SecureForm
from dynct.modules.comp.html_elements import Checkbox
from .menus import MenuRenderer

__author__ = 'justusadam'


@controller_class
class MenuAdminController:
    @controller_method('menus')
    @Regions
    def handle_menus(self, model, url):
        if len(url.path) == 1:
            return self.overview(model, url)
        elif len(url.path) == 2:
            return self.a_menu(model, url)

    def overview(self, model, url):
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
        model['content'] = SecureForm(TableElement(*l, classes={'menu-overview'}))
        model['title'] = 'Menus Overview'
        model.theme = 'admin_theme'
        return 'page'

    def a_menu(self, model,  url):
        menu_name = url.path[1]
        menu = MenuRenderer(menu_name).menu().render()
        model['content'] = List(*menu, additional={'style': 'list-style-type: none;'})
        model['title'] = get_display_name(menu_name, 'menus', 'english')
        model.theme = 'admin_theme'
        return 'page'


class Menus(ARObject):
    _table = 'menus'

    def __init__(self, id, machine_name, enabled):
        super().__init__()
        self.id = id
        self.machine_name = machine_name
        self.enabled = enabled