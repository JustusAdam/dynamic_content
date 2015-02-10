import time
import http.cookies
from framework import middleware
from framework.http import response
from . import session, users, client



__author__ = 'Justus Adam'


SESSION_TOKEN_IDENTIFIER = 'SESS'


class AuthorizationMiddleware(middleware.Handler):
    def handle_request(self, request):
        if 'Cookie' in request.headers:
            cookies = http.cookies.SimpleCookie(request.headers['Cookie'].value)
        elif 'HTTP_COOKIE' in request.headers:
            cookies = http.cookies.SimpleCookie(request.headers['HTTP_COOKIE'].value)
        else:
            request.client = client.Information(users.GUEST)
            return
        if SESSION_TOKEN_IDENTIFIER in cookies and cookies[SESSION_TOKEN_IDENTIFIER].value != session.SESSION_INVALIDATED:
            for k,v in cookies.items():
                print('k:', k, '   v:', v)
            db_result = session.validate_session(cookies[SESSION_TOKEN_IDENTIFIER].value)
            if db_result is not None:
                request.client = client.Information(db_result)
                return None
            new_cookie = http.cookies.SimpleCookie({SESSION_TOKEN_IDENTIFIER:session.SESSION_INVALIDATED})
            new_cookie[SESSION_TOKEN_IDENTIFIER]['expires'] = time.strftime("%a, %d-%b-%Y %Z %z", time.gmtime())
            return response.Redirect('/login?destination={}'.format(request.path)
                , code=303,  cookies=new_cookie)

        request.client = client.Information(users.GUEST)
