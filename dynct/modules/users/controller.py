from dynct.core.mvc.controller import Controller
from . import login
from .user_information import UserInformation, UsersOverview


__author__ = 'justusadam'



class UserController(Controller):
    def __init__(self):
        super().__init__(**{login.login_prefix: self.login, login.logout_prefix: self.logout, 'users': self.user_info})

    def user_info(self, model, url):
        if len(url.path) == 1:
            return UsersOverview(model, url).compile()
        if len(url.path) == 2:
            return UserInformation(model, url).compile()

    def login(self, model, url):
        return login.login(model, url)

    def logout(self, model, url):
        return login.logout(model, url)