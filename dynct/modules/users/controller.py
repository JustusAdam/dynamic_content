from dynct.core.mvc.controller import Controller
from . import login
from .user_information import UserInformation, UsersOverview


__author__ = 'justusadam'



class UserController(Controller):
    def __init__(self):
        super().__init__(**{login.login_prefix: login.login, login.logout_prefix: login.logout, 'users': self.user_info})

    def user_info(self, url, client):
        if len(url.path) == 1:
            return UsersOverview(url, client).compile()
        if len(url.path) == 2:
            return UserInformation(url.path[1], client).compile()