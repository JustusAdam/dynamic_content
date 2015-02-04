from ._component import Component, component, call_component, get_component, inject, inject_method, register
from . import util

@inject('settings')
def init_settings(settings):

    if settings._wrapped is None:
        from .util import config
        register(
            'settings',
            config.read_config(__file__.rsplit('/', 1)[0] + '/includes/settings.yml')
        )

init_settings()

del init_settings


from . import includes, errors, http, dchp, middleware, application, route

__author__ = 'Justus Adam'
__version__ = '0.1'
