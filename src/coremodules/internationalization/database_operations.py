from core.database_operations import Operations
from core.database import escape

__author__ = 'justusadam'


class InternationalizationOperations(Operations):

    _queries = {
        'get_display_name': 'select {language} from display_names where machine_name={machine_name} and source={source};',
        'edit_display_name': 'update display_names set {language}={value} where machine_name={machine_name} and source={source};',
        'add_item_il': 'insert into display_names (machine__name, source{languages}) values ({machine_name}, {source}{display_names});'
    }

    def get_display_name(self, item, source, language):
        self.execute('get_display_name', language=language, machine_name=escape(item), source=escape(source))
        return self.cursor.fetchone()[0]

    def edit_display_name(self, item, source, language, value):
        self.execute('edit_display_name', language=language, value=escape(value), machine_name=escape(item), source=escape(source))

    def add_item(self, item, source, translations=None):
        languages = ''
        display_names = ''
        if translations:
            for a in translations:
                languages += ', ' + a[0]
                display_names += ', ' + escape(a[1])
        self.execute('add_item_il', languages=languages, machine_name=escape(item), source=escape(source), display_names=display_names)
