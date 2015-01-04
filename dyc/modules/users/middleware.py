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
                db_result = session.validate_session(cookies[SESSION_TOKEN_IDENTIFIER].value)
                if db_result is not None:
                    request.client = client.Information(db_result)
                    return None
                return response.Redirect('/login', code=303,  cookies={SESSION_TOKEN_IDENTIFIER:''})

        request.client = client.Information(users.GUEST)