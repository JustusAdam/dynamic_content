from . import parser
from framework.util.parser import elements


__author__ = 'Justus Adam'
__version__ = '0.1'


prepend_string = """

import io as __io\n


_out = __io.StringIO()\n

if not '_print' in globals():
    _print = print

echo = print = lambda *value, sep=' ', end='', file=_out: _print(
    *value, sep=sep, end=end, file=file)\n

del __io\n
"""


def custom_compile(string):
    return compile(prepend_string + string, mode='exec', filename='<dchp>')


def custom_exec(string, context):
    exec(custom_compile(string), context)
    return context['_out'].getvalue()


def find_code(*dom_elements):
    for element in dom_elements:
        if isinstance(element, parser.DcHPElement):
            yield element
        elif isinstance(element, elements.Base):
            for a in find_code(*element.content()):
                yield a


def evaluate_dom(dom_root, context):
    context['dom'] = context['window'] = dom_root
    code = find_code(dom_root)
    for item in code:
        item.executed = custom_exec(item.code, context)
    return dom_root


def evaluate_html(string, context):
    return evaluate_dom(parser.parse(string)[0], context)


if __name__ == '__main__':
    string = 'print(\'hello\')\nout.write(\'you\')'
    c = compile(str, '<string>', 'exec')
    g = dict()
    r = exec(c, g)
    print()
