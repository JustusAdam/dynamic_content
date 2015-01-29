from dycc.backend import orm
from dycc.includes import settings

__author__ = 'Justus Adam'


def _get_table(lang):
    class Lang(orm.BaseModel):
        source_string = orm.TextField()
        translation = orm.TextField()

        class Meta:
            db_table = lang

    return Lang


class T:
    def __getattr__(self, item):
        if item in settings['supported_languages']:
            table = _get_table(item)
            table.create_table(fail_silently=True)
            setattr(self, item, table)
            return table
        else:
            raise AttributeError


_t = T() if settings['i18n_support_enabled'] is True else None

del T


def translate(source_string, language=settings['default_language']):
    if language != settings.BASE_LANGUAGE and settings.I18N_SUPPORT_ENABLED:
        db_result = getattr(_t, language).get(source_string=source_string)
        return db_result.translation if db_result else source_string
    else:
        return source_string


def edit_display_name(source_string, translation, language=settings['default_language']):
    if language != settings['base_language'] and settings['i18n_support_enabled']:
        db_result = getattr(_t, language).get(source_string=source_string)
        if db_result:
            db_result.translation = translation
            db_result.save()
        else:
            getattr(_t, language).create(source_string=source_string, translation=translation)


add_display_name = edit_display_name