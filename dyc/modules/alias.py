from dyc.backend import orm
from dyc.core import middleware


__author__ = 'justusadam'


class Alias(orm.BaseModel):
    source_url = orm.CharField()
    alias = orm.CharField(unique=True)


def translate_alias(alias):
    try:
        return Alias.get(alias=alias).source_url
    except orm.DoesNotExist as e:
        return alias


def add_alias(source, alias):
    return Alias.create(source_url=source, alias=alias)


class Middleware(middleware.Handler):
    def handle_request(self, request):
        request.path = translate_alias(request.path)