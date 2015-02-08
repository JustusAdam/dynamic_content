"""

"""
import pathlib

from ._component import Component, component, call_component, get_component, inject, inject_method, register
from . import util

__author__ = 'Justus Adam'
__version__ = '0.1'


@inject('settings')
def init_settings(settings):
    """
    Only exists to inject the settings.

    :param settings: injected settings component
    :return:
    """

    if settings._wrapped is None:
        from .util import config
        register(
            'settings',
            config.read_config(__file__.rsplit('/', 1)[0] + '/includes/settings.yml')
        )

init_settings()
del init_settings


if __name__ == '__main__':

    from . import includes, errors, http, dchp, middleware, application, route

else:
    from . import includes, errors, http, dchp, middleware, application, route
