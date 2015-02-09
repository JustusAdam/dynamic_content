import functools
from dyc.util import structures
from . import ssl


def require_ssl(function):
    """
    Decorate a controller function with this to perform a check whether an
    incoming request uses SSL

    :param function: wrapped function
    :return: None                   -> incoming request uses SSL or SSL
                                        disabled in includes.settings,
             response.Redirect(301) -> not using SSL and SSL enabled in
                                        includes.settings
    """
    @functools.wraps(function)
    def _inner(context, *args, **kwargs):
        if not isinstance(context, structures.DynamicContent):
            for arg in args:
                if isinstance(arg, structures.DynamicContent):
                    context = arg
                    break
            else:
                raise TypeError
        res = ssl.conditional_redirect(context.request)
        if res is None:
            return function(context, *args, **kwargs)
        else:
            return res
    return _inner
