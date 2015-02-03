from dycc.backend import orm
from dycc.includes import settings

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
        if item in settings.get('supported_languages', (_default_language, )):
            table = _get_table(item)
            table.create_table(fail_silently=True)
            setattr(self, item, table)
            return table
        else:
            raise AttributeError


_t = T() if settings.get('i18n_support_enabled', False) is True else None

del T


def translate(source_string, language=settings.get('default_language',_default_language)):
    if language != settings.BASE_LANGUAGE and settings.I18N_SUPPORT_ENABLED:
        db_result = getattr(_t, language).get(source_string=source_string)
        return db_result.translation if db_result else source_string
    else:
        return source_string


def edit_display_name(source_string, translation, language=settings.get('default_language', _default_language)):
    if language != settings.get('base_language', _default_language) and settings.get('i18n_support_enabled', False):
        db_result = getattr(_t, language).get(source_string=source_string)
        if db_result:
            db_result.translation = translation
            db_result.save()
        else:
            getattr(_t, language).create(source_string=source_string, translation=translation)


add_display_name = edit_display_name