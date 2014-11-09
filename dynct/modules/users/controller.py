from dynct.core.mvc.controller import Controller
from . import login
from dynct.modules.users.login import logout


__author__ = 'justusadam'



class UserController(Controller):
    def __init__(self):
        super().__init__(**{login.login_prefix: login, login.logout_prefix: logout})


