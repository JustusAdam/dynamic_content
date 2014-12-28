import datetime
from http import cookies
from urllib import error
from dynct.core.mvc import decorator
from dynct.modules.comp import html
from dynct.modules import form
from dynct.modules.commons import base
from dynct.modules.users import session

from .users import GUEST


__author__ = 'justusadam'

login_prefix = 'login'
logout_prefix = 'logout'

_cookie_time_format = '%a, %d %b %Y %H:%M:%S GMT'

USERNAME_INPUT = html.Label('Username', label_for='username'), html.Input(name='username', required=True)
PASSWORD_INPUT = html.Label('Password', label_for='password'), html.Input(input_type='password', required=True, name='password')

LOGOUT_TARGET = '/login'

LOGOUT_BUTTON = html.ContainerElement('Logout', html_type='a', classes={'logout', 'button'},
                                 additional={'href': '/' + logout_prefix})

LOGIN_FORM = form.SecureForm(
    html.TableElement(
        USERNAME_INPUT,
        PASSWORD_INPUT
    )
    , action='/' + login_prefix, classes={'login-form'}, submit=html.SubmitButton(value='Login')
)

LOGIN_COMMON = form.SecureForm(
    html.ContainerElement(
        *USERNAME_INPUT + PASSWORD_INPUT
    )
    , action='/' + login_prefix, classes={'login-form'}, submit=html.SubmitButton(value='Login')
)


class LoginCommonHandler(base.Commons):
    source_table = 'user_management'

    def get_content(self, name):
        return LOGIN_COMMON


@decorator.controller_function('login', '$|(/?failed)', get=False, post=False)
def login(model, failed):
    message = html.ContainerElement('Your Login failed, please try again.', classes={'alert'}) if failed else ''
    model['content'] = html.ContainerElement(message, LOGIN_FORM)
    return 'page'


@decorator.controller_function('login', '$', get=False, post=['username', 'password'])
def login(model, username, password):
    if not model.client.check_permission('access login page'):
        raise error.HTTPError('/login', 403, None, None, None)
    username = username[0]
    password = password[0]
    token = session.start_session(username, password)
    if token:
        cookie = cookies.SimpleCookie({'SESS': token})
        model.cookies = cookie
        return ':redirect:/'
    else:
        return ':redirect:/login/failed'




def logout(model, url):
    user = model.client.user
    if user == GUEST:
        return ':redirect:/login'
    else:
        session.close_session(user)
        time = datetime.datetime.utcnow() - datetime.timedelta(days=1)

        if 'destination' in url.get_query:
            dest = url.get_query['destination'][0]
        else:
            dest = '/'
        model.cookies.load({'SESS': ''})
        model.cookies['SESS']['expires'] = time.strftime(_cookie_time_format)
        return ':redirect:' + dest