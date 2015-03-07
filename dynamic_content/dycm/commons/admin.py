from framework import route
from framework.util import html
from dycm import i18n, theming
from framework.middleware import csrf
from . import model as _model, menus as _menus, decorator

__author__ = 'Justus Adam'


@route.controller_class
class MenuAdminController:
    @route.controller_method('menus')
    @theming.breadcrumbs
    @decorator.Regions
    def overview(self, dc_obj):
        menus = _model.Menu.select()
        l = [
            [
                html.A(item.id, href='menus/' + item.machine_name),
                html.A(i18n.translate(item.machine_name), href='menus/' + item.machine_name),
                html.Checkbox(checked=bool(item.enabled))
            ] for item in menus]
        dc_obj.context['content'] = csrf.SecureForm(html.TableElement(*l, classes={'menu-overview'}))
        dc_obj.context['title'] = 'Menus Overview'
        dc_obj.config['theme'] = 'admin_theme'
        return 'page'

    @route.controller_method('menus/{str}')
    @theming.breadcrumbs
    @decorator.Regions
    def a_menu(self, dc_obj, menu_name):
        menu = _menus.menu(menu_name).render()
        dc_obj.context['content'] = html.List(*menu, additional={'style': 'list-style-type: none;'})
        dc_obj.context['title'] = i18n.translate(menu_name)
        dc_obj.config['theme'] = 'admin_theme'
        return 'page'
