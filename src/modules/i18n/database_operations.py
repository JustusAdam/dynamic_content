from core.database_operations import Operations
from backend.database import escape


__author__ = 'justusadam'

baselang = 'english'


class DisplayNamesOperations(Operations):
    _queries = {
        'mysql': {
            'get_display_name': 'select {language} from display_names where machine_name={machine_name} and source_table={source_table};',
            'edit_display_name': 'update display_names set {language}={value} where machine_name={machine_name} and source_table={source_table};',
            'add_item_il': 'insert into display_names (machine_name, source_table{languages}) values ({machine_name}, {source_table}{display_names});'
        }
    }

    _tables = ['display_names']

    def get_display_name(self, item, source_table, language):
        machine_name = escape(item)
        source_table = escape(source_table)
        self.execute('get_display_name', language=language, machine_name=machine_name, source_table=source_table)
        result = self.cursor.fetchone()
        if result:
            return result[0]
        elif language != baselang:
            self.execute('get_display_name', language=baselang, machine_name=machine_name, source_table=source_table)
            result = self.cursor.fetchone()
            if result:
                return result[0]
        return item

    def edit_display_name(self, item, source_table, language, value):
        result = self.get_display_name(item, source_table, language)
        if result == item:
            self.add_item(item, source_table, [language, value])
        else:
            self.execute('edit_display_name', language=language, value=escape(value), machine_name=escape(item),
                         source_table=escape(source_table))

    def add_item(self, item, source_table, *translations):
        languages = ''
        display_names = ''
        if translations:
            for (language, value) in translations:
                languages += ', ' + language
                display_names += ', ' + escape(value)
        self.execute('add_item_il', languages=languages, machine_name=escape(item), source_table=escape(source_table),
                     display_names=display_names)
