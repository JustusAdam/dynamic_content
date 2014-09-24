from .login import LoginHandler

__author__ = 'justusadam'


name = 'user_management'

role = 'user_management'

login_prefix = 'login'


def content_handler(url):
    return LoginHandler(url)


def prepare():
    from core.database_operations import ContentHandlers
    cho = ContentHandlers()
    cho.add_new('login', 'user_management', login_prefix)