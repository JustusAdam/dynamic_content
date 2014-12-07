from dynct.backend.orm import *
from dynct.includes.settings import SUPPORTED_LANGUAGES, DEFAULT_LANGUAGE

__author__ = 'justusadam'


def _get_table(lang):
    class Lang(BaseModel):
        source_string = TextField()
        translation = TextField()

        class Meta:
            db_table = lang
    return Lang


class T:
    def __getattr__(self, item):
        if item in SUPPORTED_LANGUAGES:
            table = _get_table(item)
            table.create_table(fail_silently=True)
            setattr(self, item, table)
            return table
        else:
            raise AttributeError


_t = T()

del T

def translate(source_string, language=DEFAULT_LANGUAGE):
    db_result = getattr(_t, language).get(source_string=source_string)
    return db_result.translation if db_result else source_string


def edit_display_name(source_string, translation, language=DEFAULT_LANGUAGE):
    db_result = getattr(_t, language).get(source_string=source_string)
    if db_result:
        db_result.translation = translation
        db_result.save()
    else:
        getattr(_t, language).create(source_string=source_string, translation=translation)


add_display_name = edit_display_name