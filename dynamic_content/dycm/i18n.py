from framework.backend import orm
from framework.includes import get_settings

__author__ = 'Justus Adam'


_default_language = 'en'


def _get_table(lang):
    class Lang(orm.BaseModel):
        source_string = orm.TextField()
        translation = orm.TextField()

        class Meta:
            db_table = lang

    return Lang


class T:
    def __getattr__(self, item):
        if item in get_settings().get('supported_languages', (_default_language, )):
            table = _get_table(item)
            table.create_table(fail_silently=True)
            setattr(self, item, table)
            return table
        else:
            raise AttributeError


_t = T() if get_settings().get('i18n_support_enabled', False) is True else None

del T


def translate(source_string, language=get_settings().get('default_language',_default_language)):
    if language != get_settings().BASE_LANGUAGE and get_settings().I18N_SUPPORT_ENABLED:
        db_result = getattr(_t, language).get(source_string=source_string)
        return db_result.translation if db_result else source_string
    else:
        return source_string


def edit_display_name(source_string, translation, language=get_settings().get('default_language', _default_language)):
    if language != get_settings().get('base_language', _default_language) and get_settings().get('i18n_support_enabled', False):
        db_result = getattr(_t, language).get(source_string=source_string)
        if db_result:
            db_result.translation = translation
            db_result.save()
        else:
            getattr(_t, language).create(source_string=source_string, translation=translation)


add_display_name = edit_display_name