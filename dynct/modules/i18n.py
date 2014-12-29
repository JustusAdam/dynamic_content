from dynct.backend import orm
from dynct.includes import settings

__author__ = 'justusadam'


def _get_table(lang):
    class Lang(orm.BaseModel):
        source_string = orm.TextField()
        translation = orm.TextField()

        class Meta:
            db_table = lang

    return Lang


class T:
    def __getattr__(self, item):
        if item in settings.SUPPORTED_LANGUAGES:
            table = _get_table(item)
            table.create_table(fail_silently=True)
            setattr(self, item, table)
            return table
        else:
            raise AttributeError


_t = T() if settings.I18N_SUPPORT_ENABLED else None

del T


def translate(source_string, language=settings.DEFAULT_LANGUAGE):
    if language != settings.BASE_LANGUAGE and settings.I18N_SUPPORT_ENABLED:
        db_result = getattr(_t, language).get(source_string=source_string)
        return db_result.translation if db_result else source_string
    else:
        return source_string


def edit_display_name(source_string, translation, language=settings.DEFAULT_LANGUAGE):
    if language != settings.BASE_LANGUAGE and settings.I18N_SUPPORT_ENABLED:
        db_result = getattr(_t, language).get(source_string=source_string)
        if db_result:
            db_result.translation = translation
            db_result.save()
        else:
            getattr(_t, language).create(source_string=source_string, translation=translation)


add_display_name = edit_display_name