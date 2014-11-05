from .ar import DisplayName

__author__ = 'justusadam'


def prepare():
    pass


def get_display_name(item, source_table, language):
    return getattr(DisplayName.get(machine_name=item, source_table=source_table), language)


def edit_display_name(item, source_table, language, value):
    a = DisplayName.get(machine_name=item, source_table=source_table)
    setattr(a, language, value)
    a.save()


add_display_name = edit_display_name


def add_item(item, source_table, translations):
    DisplayName(item, source_table, translations).save()