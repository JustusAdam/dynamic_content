import io
import functools
from . import parser
from dyc.util import html as _html


prepend_string = """

import functools\n
import io\n


_out = io.StringIO()\n

echo = print = functools.partial(print, file=_out, end='')\n

del functools, io\n
"""


def custom_compile(string):
    return compile(prepend_string + string, mode='exec', filename='<pyhp>')


def custom_exec(string, context):
    exec(custom_compile(string), context)
    return context['_out'].getvalue()


def find_code(*dom_elements):
    for element in dom_elements:
        if isinstance(element, parser.PyHPElement):
            yield element
        elif isinstance(element, _html.ContainerElement):
            yield from find_code(*element.content)


def evaluate_dom(dom_root, context):
    context['dom'] = dom_root
    code = find_code(dom_root)
    for item in code:
        item.executed = custom_exec(item.code, context)
    return dom_root


def evaluate_html(string, context):
    return evaluate_dom(parser.parse(string)[0], context)


if __name__ == '__main__':
    string = 'print(\'hello\')\nout.write(\'you\')'

    g = dict()
    r = exec(c, g)
    print()
