from application.config import ModuleConfig
from application.fragments import AppFragment
from .database_operations import DisplayNamesOperations

__author__ = 'justusadam'


class I18n(AppFragment):

    def __init__(self, config):
        super().__init__(config)
        self.ops = DisplayNamesOperations()

    def add_item(self, item, source_table, translations):
        if not translations:
            translations = []
        elif isinstance(translations, dict):
            translations = [(k, translations[k]) for k in translations]
        elif isinstance(translations[0], str):
            translations = [translations]
        self.ops.add_item(item, source_table, *translations)

    def get_display_name(self, item, source_table, language):
        return self.ops.get_display_name(item, source_table, language)

    def edit_display_name(self, item, source_table, language, value):
        self.ops.edit_display_name(item, source_table, language, value)

    add_display_name = edit_display_name

    def setup_fragment(self):
        self.ops.init_tables()


class I18nConf(ModuleConfig):
    pass