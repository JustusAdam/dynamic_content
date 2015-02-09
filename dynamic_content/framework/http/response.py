from http import cookies as _cookies
import collections
from . import headers as h_mod


__author__ = 'Justus Adam'
__version__ = '0.1'


# HTTP Responecodes as defined in RFC 2616 neatly accessible via field names
# For further information on use and meaning of these responses please refer to
# http://www.w3.org/Protocols/rfc2616/rfc2616-sec10.html
HttpResponseCodes = (collections.namedtuple('ResponseCodeContainer', ('Continue',
'SwitchingProtocols', 'OK', 'Created', 'Accepted',
'NonAuthoritativeInformation','NoContent', 'ResetContent', 'PartialContent',
'MultipleChoices', 'MovedPermanently', 'Found', 'SeeOther', 'NotModified',
'UseProxy', 'TemporaryRedirect', 'BadRequest', 'Unauthorized',
'PaymentRequired', 'Forbidden', 'NotFound', 'MethodNotAllowed', 'NotAcceptable',
'ProxyAuthenticationRequired', 'RequestTimeout', 'Conflict', 'Gone',
'LengthRequired', 'PreconditionFailed', 'RequestEntityTooLarge',
'RequestURITooLong', 'UnsupportedMediaType', 'RequestedRangeNotSatisfiable',
'ExpectationFailed', 'ImATeapot', 'InternalServerError', 'NotImplemented',
'BadGateway', 'ServiceUnavailable', 'GatewayTimeout', 'HTTPVersionNotSupported')
)(
Continue = 100,
SwitchingProtocols = 101,
OK = 200,
Created = 201,
Accepted = 202,
NonAuthoritativeInformation = 203,
NoContent = 204,
ResetContent = 205,
PartialContent = 206,
MultipleChoices = 300,
MovedPermanently = 301,
Found = 302,
SeeOther = 303,
NotModified = 304,
UseProxy = 305,
TemporaryRedirect = 307,
BadRequest = 400,
Unauthorized = 401,
PaymentRequired = 402,
Forbidden = 403,
NotFound = 404,
MethodNotAllowed = 405,
NotAcceptable = 406,
ProxyAuthenticationRequired = 407,
RequestTimeout = 408,
Conflict = 409,
Gone = 410,
LengthRequired = 411,
PreconditionFailed = 412,
RequestEntityTooLarge = 413,
RequestURITooLong = 414,
UnsupportedMediaType = 415,
RequestedRangeNotSatisfiable = 416,
ExpectationFailed = 417,
ImATeapot=418,
InternalServerError = 500,
NotImplemented = 501,
BadGateway = 502,
ServiceUnavailable = 503,
GatewayTimeout = 504,
HTTPVersionNotSupported = 505
))


class Response(object):
    def __init__(self, body=None, code=200, headers:dict=None, cookies=None):
        self.body = body
        self.code = code
        self.headers = h_mod.HeaderMap(headers) if not headers is None else h_mod.HeaderMap()
        if (isinstance(cookies, dict)
            and cookies
            and not isinstance(cookies, _cookies.BaseCookie)):
            cookies = _cookies.SimpleCookie(cookies)
        if cookies is None:
            cookies = _cookies.SimpleCookie()
        elif cookies:
            self.headers['Set-Cookie'] = cookies.output(header='')[1:]
        self.cookies = cookies


class Redirect(Response):
    def __init__(self, location, code=HttpResponseCodes.Found,
                headers=None, cookies=None):
        if not code in (
            HttpResponseCodes.MovedPermanently,
            HttpResponseCodes.Found,
            HttpResponseCodes.SeeOther
            ):
            raise TypeError('Expected code 301 or 302, got {}'.format(code))
        headers = headers if headers is not None else {}
        headers['Location'] = location
        super().__init__(code=code, cookies=cookies, headers=headers, body=None)
