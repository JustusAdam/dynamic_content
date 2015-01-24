import datetime
from http import cookies

from dyc import dchttp
from dyc import modules
from dyc.util import html, console
from dyc.core import mvc
from dyc.middleware import csrf
commons, theming = modules.import_modules('commons', 'theming')
from . import session, users, decorator


__author__ = 'Justus Adam'

login_prefix = 'login'
logout_prefix = 'logout'

_cookie_time_format = '%a, %d %b %Y %H:%M:%S GMT'

USERNAME_INPUT = (
    html.Label('Username', label_for='username'),
    html.Input(name='username', required=True)
    )
PASSWORD_INPUT = (
    html.Label('Password', label_for='password'),
    html.Input(input_type='password', required=True,name='password')
    )

LOGOUT_TARGET = '/login'

LOGOUT_BUTTON = html.ContainerElement(
    'Logout',
    html_type='a',
    classes={'logout', 'button'},
    additional={'href': '/' + logout_prefix}
    )

LOGIN_FORM = csrf.SecureForm(
    html.TableElement(
        USERNAME_INPUT,
        PASSWORD_INPUT
    ),
    action='/' + login_prefix,
    classes={'login-form'},
    submit=html.SubmitButton(value='Login')
)

LOGIN_COMMON = csrf.SecureForm(
    html.ContainerElement(
        *USERNAME_INPUT + PASSWORD_INPUT
    ),
    action='/' + login_prefix,
    classes={'login-form'},
    submit=html.SubmitButton(value='Login')
)


@commons.implements('login')
class LoginCommonHandler(commons.Handler):
    source_table = 'user_management'

    def get_content(self, conf, render_args, client):
        return LOGIN_COMMON


@mvc.controller_function({'login'}, method=dchttp.RequestMethods.GET, query=True, require_ssl=True)
@decorator.authorize('access login page')
@theming.breadcrumbs
@commons.Regions
def login(dc_obj, query, failed=False):
    print(query)
    message = html.ContainerElement('Your Login failed, please try again.', classes={'alert'}) if failed else ''
    dc_obj.context['content'] = html.ContainerElement(message, LOGIN_FORM)
    dc_obj.context['title'] = 'Login'
    return 'page'


@mvc.controller_function('login', method=dchttp.RequestMethods.POST, query=['username', 'password'])
@decorator.authorize('access login page')
def login(dc_obj, username, password):
    username = username[0]
    password = password[0]
    token = session.start_session(username, password)
    if token:
        cookie = cookies.SimpleCookie({'SESS': token})
        dc_obj.config['cookies'] = cookie
        return ':redirect:/'
    else:
        return ':redirect:/login/failed'


@mvc.controller_function(
    'logout',
    method=dchttp.RequestMethods.GET,
    query=True
    )
def logout(dc_obj, query):
    user = dc_obj.request.client.user
    if user == users.GUEST:
        return ':redirect:/login'
    else:
        session.close_session(user)
        time = datetime.datetime.utcnow() - datetime.timedelta(days=1)

        if 'destination' in query:
            dest = query['destination'][0]
        else:
            dest = '/'
        dc_obj.config.setdefault(
            'cookies',
            cookies.SimpleCookie()).load({'SESS': ''}
            )
        dc_obj.config['cookies']['SESS']['expires'] = time.strftime(_cookie_time_format)
        return ':redirect:' + dest
