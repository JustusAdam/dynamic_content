import functools
from framework.util import structures


__author__ = 'Justus Adam'
__version__ = '0.1'


def apply_to_context(
    apply_before=True,
    return_from_decorator=False,
    with_return=False
    ):
    """
    Apply the outer decorated function to the inner decorated
    functions first argument
    
    :param apply_before:
    :param return_from_decorator:
    :param with_return:
    :return:
    """
    def wrapper(func):
        def inner_wrapper(inner_func):

            @functools.wraps(inner_func)
            def inner_call(*args, **kwargs):
                context = (
                    args[0]
                    if isinstance(args[0], structures.DynamicContent)
                    else args[1]
                    )
                if apply_before:
                    res_dec = func(context)
                    res = inner_func(*args, **kwargs)

                else:
                    res = inner_func(*args, **kwargs)
                    if with_return:
                        res_dec = func(context, res)
                    else:
                        res_dec = func(context)

                if return_from_decorator:
                    return res_dec
                else:
                    return res

            return inner_call
        return inner_wrapper
    return wrapper
