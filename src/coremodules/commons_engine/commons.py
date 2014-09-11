from core.database import escape_item

__author__ = 'justusadam'


class MenuHandler:

    def __init__(self, name, db):
        self.db = db
        self.name = name

    def get_items(self):
        db_result = self.db.select('menu_items', ('display_name', 'item_path'), 'where enabled=true and menu=' + escape_item(self.name, 'utf-8'))
        if not db_result:
            return False
        else:
            return db_result.fetchall()