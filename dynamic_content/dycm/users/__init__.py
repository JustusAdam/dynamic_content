from framework.includes import settings
from . import users, model, client, session, decorator , middleware


if settings.get('use_login_page', False):
    from . import login

__author__ = 'Justus Adam'


START_REGION = 'sidebar_left'

START_THEME = 'default_theme'
