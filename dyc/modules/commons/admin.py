from dyc.core.mvc import decorator as mvc_decorator
from dyc.modules.comp import decorator as comp_decorator
from dyc.util import html
from dyc.modules import i18n
from dyc.modules import anti_csrf
from . import model as _model, menus as _menus

__author__ = 'Justus Adam'


@mvc_decorator.controller_class
class MenuAdminController:
    @mvc_decorator.controller_method('menus')
    @comp_decorator.Regions
    def handle_menus(self, model, url):
        if len(url.path) == 1:
            return self.overview(model, url)
        elif len(url.path) == 2:
            return self.a_menu(model, url)

    def overview(self, model, url):
        menus = _model.Menu.select()
        l = [
            [
                html.A(str(url.path) + '/' + item.machine_name, item.id),
                html.A(str(url.path) + '/' + item.machine_name, i18n.translate(item.display_name)),
                html.Checkbox(checked=bool(item.enabled))
            ] for item in menus]
        model['content'] = anti_csrf.SecureForm(html.TableElement(*l, classes={'menu-overview'}))
        model['title'] = 'Menus Overview'
        model.theme = 'admin_theme'
        return 'page'

    def a_menu(self, model, url):
        menu_name = url.path[1]
        menu = _menus.menu(menu_name).render()
        model['content'] = html.List(*menu, additional={'style': 'list-style-type: none;'})
        model['title'] = i18n.translate(menu_name)
        model.theme = 'admin_theme'
        return 'page'