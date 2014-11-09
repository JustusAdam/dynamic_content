from dynct.core.mvc.controller import Controller
from . import login


__author__ = 'justusadam'



class UserController(Controller):
    def __init__(self):
        super().__init__(**{login.login_prefix: login.login, login.logout_prefix: login.logout})