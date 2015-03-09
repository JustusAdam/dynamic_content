import unittest
from dycm import commons
from dycm.commons import menus, admin
import nose

__author__ = 'Justus Adam'
__version__ = '0.1'


class TestMenus(unittest.TestCase):
    def setUp(self):
        commons.model.MenuItem.drop_table(fail_silently=True)
        commons.model.Menu.drop_table(fail_silently=True)

        commons.model.Menu.create_table()
        commons.model.MenuItem.create_table()

        self.menu_1_name = 'testmenu'
        self.menu_1_db_repr = commons.model.Menu.create(
            machine_name=self.menu_1_name, enabled=True
        )

        # name, path, child_enabled, parent, weight
        self.menu_1_root = '<root>', '', True, None, 1
        self.menu_1_item_1 = 'item-1', 'item/1', True, '<root>', 0
        self.menu_1_item_2 = 'item-2', 'item/2', False, '<root>', 3

        for name, path, enabled, parent, weight in (
            self.menu_1_root,
            self.menu_1_item_1,
            self.menu_1_item_2
        ):
            commons.model.MenuItem.create(
                display_name=name,
                path=path,
                menu=self.menu_1_db_repr,
                enabled=enabled,
                parent=commons.model.MenuItem.get(display_name=parent) if parent else None,
                weight=weight
            )

    def test_menu_exists(self):
        self.assertEqual(
            commons.model.Menu.get(machine_name=self.menu_1_name),
            self.menu_1_db_repr
        )

    def test_menu_render(self):
        compiled = menus.menu(self.menu_1_name)
        rendered = compiled.render_children(0)

        self.assertEqual(
            rendered,
            '<ul class="menu">'
                '<li class="layer-0">'
                    '<a href="{}">{}</a>'
                '</li>'
            '</ul>'.format(self.menu_1_item_1[1], self.menu_1_item_1[0])
        )