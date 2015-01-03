import peewee
from dyc.dchttp import response
from dyc.core import middleware
from . import session, users, client
import http.cookies

__author__ = 'justusadam'


SESSION_TOKEN_IDENTIFIER = 'SESS'


@middleware.register
class AuthorizationMiddleware(middleware.Handler):
    def handle_request(self, request):
        if 'Cookie' in request.headers:
            cookies = http.cookies.SimpleCookie(request.headers['Cookie'])
            if SESSION_TOKEN_IDENTIFIER in cookies:
                try:
                    db_result = session.validate_session(cookies[SESSION_TOKEN_IDENTIFIER].value)
                    if db_result is not None:
                        user = db_result
                        request.client = client.Information(user)
                        return None
                except peewee.DoesNotExist:
                    return response.Redirect('/login', cookies={SESSION_TOKEN_IDENTIFIER:''})

        request.client = client.Information(users.GUEST)