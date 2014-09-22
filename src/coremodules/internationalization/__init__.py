from .database_operations import DisplayNamesOperations

__author__ = 'justusadam'


def prepare():
    DisplayNamesOperations().init_tables()


Operations = DisplayNamesOperations


def get_display_name(item, source_table, language):
    return DisplayNamesOperations().get_display_name(item, source_table, language)


def edit_display_name(item, source_table, language, value):
    DisplayNamesOperations().edit_display_name(item, source_table, language, value)


add_display_name = edit_display_name


def add_item(item, source_table, translations):
    if not translations:
        translations = None
    elif isinstance(translations, dict):
        translations = [(k,translations[k]) for k in translations]
    elif isinstance(translations[0], str):
        translations = [translations]
    DisplayNamesOperations().add_item(item, source_table, translations)