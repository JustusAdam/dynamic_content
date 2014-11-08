from dynct.core.mvc.controller import Controller
from dynct.core.mvc.model import Model
from .login import *

__author__ = 'justusadam'


class UserController(Controller):
    def __init__(self):
        super().__init__(**{login_prefix:self.login, logout_prefix: self.logout})

    def login(self, url, client):
        return LoginHandler(url, client).compile()

    def logout(self, url, client):
        user = client.user
        if user == GUEST:
            m = Model(':redirect:')
            m.headers.add(('Location', '/login'))
            return m
        else:
            session.close_session(user)
            time = datetime.datetime.utcnow() - datetime.timedelta(days=1)
            m = Model(':redirect:')
            if 'destination' in url.get_query:
                dest = url.get_query['destination'][0]
            else:
                dest = '/'
            m.headers.add(('Location', dest))
            m.cookies.load({'SESS': ''})
            m.cookies['SESS']['expires'] = time.strftime(_cookie_time_format)
            return m