"""Context dct related infrastructure"""
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

    :param apply_before: apply the decorated function first (boolean)
    :param return_from_decorator: overall return value is the wrapped
                                    function return (boolean)
    :param with_return: call the wrapped function with context & return from
                        the innermost function (only if not apply_before=True)
    :return: depends
    """
    def wrapper(func):
        """
        apply_to_context's outer wrapper function

        :param func: function to apply to context
        :return: inner_wrapper
        """
        def inner_wrapper(inner_func):
            """
            apply_to_context's inner wrapping function

            :param inner_func: innermost wrapped function
            :return: generated decorator
            """

            @functools.wraps(inner_func)
            def inner_call(*args, **kwargs):
                """
                apply_to_context's inner wrapping function
                captures call arguments and executes actual logic

                :param args: inner wrapped func call args
                :param kwargs: inner wrapped func call kwargs
                :return: depends
                """
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
