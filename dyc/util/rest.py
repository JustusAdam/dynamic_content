from dyc import dchttp

__author__ = 'Justus Adam'

import inspect
import json


def _object_transform(o):
    items = filter(
        (lambda a: not a.startswith('_') and not a in o.__private__)
        if hasattr(o, '__private__') else
        (lambda a: not a.startswith('_'))
        , dir(o))

    def _items():
        for k in items:
            v = getattr(o, k)
            if (not inspect.isfunction(v)
                and not inspect.ismethod(v)
                and not inspect.isclass(v)):
                yield k, v

    return {
        k: v
        for k, v in _items()

    }


json_transform = lambda a: json.dumps(a, default=_object_transform)


def json_response(content, context):
    return dchttp.response.Response(
        code=200,
        body=json_transform(content),
        headers=(
            context.config['headers']
            if 'headers' in context.config
            and context.config['headers'] is not None
            else {}
            ),
        cookies=(
            context.config['cookies']
            if 'cookies' in context.config
            and context.config is not None
            else {}
            )
    )