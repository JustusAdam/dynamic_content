from http.cookies import SimpleCookie

__author__ = 'justusadam'


class Response(object):
    def __init__(self, body=None, code=200, headers={}, cookies=None):
        self.body = body
        self.code = code
        self.headers = headers
        if isinstance(cookies, dict) and cookies:
            cookies = SimpleCookie.load(SimpleCookie(), cookies)
        if cookies is None:
            cookies = SimpleCookie()
        else:
            self.headers['Set-Cookie'] = cookies.output(header='')[1:]
        self.cookies = cookies


class Redirect(Response):
    def __init__(self, location, code=302, headers={}, cookies=None):
        if not code in (302, 301, 303):
            raise TypeError('Expected code 301 or 302, got ' + str(code))
        headers['Location'] = location
        super().__init__(code=code, cookies=cookies, headers=headers, body=None)