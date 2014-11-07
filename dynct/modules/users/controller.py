from dynct.core.mvc.controller import Controller
from .login import *

__author__ = 'justusadam'


class UserController(Controller):
    def __init__(self):
        super().__init__(**{login_prefix:self.login, logout_prefix: self.logout})

    def login(self, url, client):
        return LoginHandler(url, client).compile

    def logout(self, url, client):
        return LogoutHandler(url, client).compile