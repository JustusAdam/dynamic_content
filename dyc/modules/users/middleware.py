from dyc.dchttp import response
from dyc.core import middleware
from . import session, users, client
import http.cookies
import time


__author__ = 'Justus Adam'


SESSION_TOKEN_IDENTIFIER = 'SESS'

SESSION_INVALIDATED = 'invalid'


@middleware.register
class AuthorizationMiddleware(middleware.Handler):
    def handle_request(self, request):
        if 'Cookie' in request.headers:
            cookies = http.cookies.SimpleCookie(request.headers['Cookie'])
        elif 'HTTP_COOKIE' in request.headers:
            cookies = http.cookies.SimpleCookie(request.headers['HTTP_COOKIE'])
        else:
            request.client = client.Information(users.GUEST)
            return
        if SESSION_TOKEN_IDENTIFIER in cookies and cookies[SESSION_TOKEN_IDENTIFIER] != SESSION_INVALIDATED:
            db_result = session.validate_session(cookies[SESSION_TOKEN_IDENTIFIER].value)
            if db_result is not None:
                request.client = client.Information(db_result)
                return None
            new_cookie = http.cookies.SimpleCookie({SESSION_TOKEN_IDENTIFIER:SESSION_INVALIDATED})
            new_cookie['SESS']['expires'] = time.strftime("%a, %d-%b-%Y %T GMT", time.gmtime())
            return response.Redirect('/login', code=303,  cookies=new_cookie)

        request.client = client.Information(users.GUEST)
