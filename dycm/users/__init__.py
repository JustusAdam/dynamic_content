from dycc.includes import settings
from . import users, model, client, session, decorator , middleware


if settings['use_login_page']:
    from . import login

__author__ = 'Justus Adam'


START_REGION = 'sidebar_left'

START_THEME = 'default_theme'
