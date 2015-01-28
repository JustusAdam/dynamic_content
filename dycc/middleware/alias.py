from dycc.backend import orm
from dycc import middleware


__author__ = 'Justus Adam'


class Alias(orm.BaseModel):
    source_url = orm.CharField()
    alias = orm.CharField(unique=True)


def translate_alias(alias):
    try:
        return Alias.get(alias=alias).source_url
    except orm.DoesNotExist:
        return alias


def add_alias(source, alias):
    return Alias.create(source_url=source, alias=alias)


class Middleware(middleware.Handler):
    def handle_request(self, request):
        request.path = translate_alias(request.path)
