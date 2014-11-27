from . import login
from dynct.core.mvc.decorator import controller_class, controller_method
from .user_information import UserInformation, UsersOverview


__author__ = 'justusadam'



@controller_class
class UserController:
    @controller_method('user')
    def user_info(self, model, url):
        if len(url.path) == 1:
            return UsersOverview(model, url).compile()
        if len(url.path) == 2:
            return UserInformation(model, url).compile()

    @controller_method('logout')
    def logout(self, model, url):
        return login.logout(model, url)