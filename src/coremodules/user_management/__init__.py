from core.database_operations import ContentHandlers

__author__ = 'justusadam'


name = 'user_management'

role = 'user_management'

login_prefix = 'login'


def prepare():
    cho = ContentHandlers()
    cho.add_new('login', 'user_management', login_prefix)