from framework.includes import get_settings
from . import users, model, client, session, decorator , middleware


if get_settings().get('use_login_page', False):
    from . import login

__author__ = 'Justus Adam'


START_REGION = 'sidebar_left'

START_THEME = 'default_theme'
