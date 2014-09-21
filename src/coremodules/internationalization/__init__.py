from .database_operations import DisplayNamesOperations

__author__ = 'justusadam'

dn_ops = DisplayNamesOperations()


def get_display_name(item, source, language):
    return dn_ops.get_display_name(item, source, language)



def edit_display_name(item, source, language, value):
    dn_ops.edit_display_name(item, source, language, value)


add_display_name = edit_display_name


def add_item(item, source, translations):
    if not translations:
        translations = None
    elif isinstance(translations, dict):
        translations = [(k,translations[k] for k in translations)]
    elif isinstance(translations[0], str):
        translations = [translations]
    dn_ops.add_item(item, source, translations)