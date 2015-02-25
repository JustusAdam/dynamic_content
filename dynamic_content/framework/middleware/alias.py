"""Implementation for defining and resolving page aliases"""

from framework.backend import orm
from framework import middleware


__author__ = 'Justus Adam'


class Alias(orm.BaseModel):
    """
    Mapping an alias to a source url
    """
    source_url = orm.CharField()
    alias = orm.CharField(unique=True)


def translate_alias(alias):
    """
    Find the source url for a given alias (if it exists)

    :param alias: alias url
    :return: source (will be alias if none exists)
    """
    try:
        return Alias.get(alias=alias).source_url
    except orm.DoesNotExist:
        return alias


def add_alias(source, alias):
    """
    Add a new alias to the database

    :param source:
    :param alias:
    :return: created Alias object
    """
    return Alias.create(source_url=source, alias=alias)


class Middleware(middleware.Handler):
    """
    Alias resolving middleware

    Rewrites the request.path if it was an alias
    """
    def handle_request(self, request):
        """
        Overwritten parent method

        :param request:
        :return: None
        """
        request.path = translate_alias(request.path)
