from dynct.core.mvc.decorator import controller_class, controller_method
from dynct.modules.comp.decorator import Regions
from dynct.modules.comp.html import TableElement, List, A
from dynct.modules.i18n import translate
from dynct.modules.form.secure import SecureForm
from dynct.modules.comp.html import Checkbox
from .menus import menu as _menu
from .model import Menu

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
        menus = Menu.select()
        l = [
                [
                    A(str(url.path) + '/' + item.machine_name, item.id),
                    A(str(url.path) + '/' + item.machine_name, translate(item.display_name)),
                    Checkbox(checked=bool(item.enabled))
                ] for item in menus]
        model['content'] = SecureForm(TableElement(*l, classes={'menu-overview'}))
        model['title'] = 'Menus Overview'
        model.theme = 'admin_theme'
        return 'page'

    def a_menu(self, model,  url):
        menu_name = url.path[1]
        menu = _menu(menu_name).render()
        model['content'] = List(*menu, additional={'style': 'list-style-type: none;'})
        model['title'] = translate(menu_name)
        model.theme = 'admin_theme'
        return 'page'