"""Evaluate dhcp codeblocks"""
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
    """
    Compile with predefined settings

    :param string: string to compile
    :return:
    """
    return compile(prepend_string + string, mode='exec', filename='<dchp>')


def custom_exec(string, context):
    """
    Execute the code, capturing the print() and echo()

    :param string: code to execute as string
    :param context: global() variables for the code
    :return: print() and echo() output
    """
    exec(custom_compile(string), context)
    return context['_out'].getvalue()


def find_code(dom_elements):
    """
    Find code blocks in the html tree

    :param dom_elements: html_tree
    :return: yielding dhcp code elements
    """
    for element in dom_elements:
        if isinstance(element, parser.DcHPElement):
            yield element
        elif isinstance(element, elements.Base):
            for a in find_code(element.content()):
                yield a


def evaluate_dom(dom_root, context):
    """
    Take a dom root and a context and compile the contained code and run it

    :param dom_root: the html dom tree
    :param context: context variable
    :return: dom_root with executed code
    """
    context['dom'] = context['window'] = dom_root
    code = find_code((dom_root,))
    for item in code:
        item.executed = custom_exec(item.code, context)
    return dom_root


def evaluate_html(string, context):
    """
    Take html input, parse it and evaluate all code fragments contained

    :param string: html document
    :param context: context for the evaluation
    :return: dom root element
    """
    return evaluate_dom(parser.parse(string)[0], context)