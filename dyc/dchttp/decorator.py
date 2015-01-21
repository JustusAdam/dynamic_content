import functools
from dyc.includes import settings
from dyc.core import mvc
from . import response, ssl


def require_ssl(function):
	@functools.wraps(function)
	def _inner(context, *args, **kwargs):
		if not isinstance(context, mvc.context.Context):
			for arg in args:
				if isinstance(arg, mvc.context.Context):
					context = arg
					break
			else:
				raise TypeError
		res = ssl.conditional_redirect(context.request)
		if res is None:
			return function(context, *args, **kwargs)
		else:
			return res