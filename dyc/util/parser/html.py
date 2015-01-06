import functools
from . import generic
from .. import html


__author__ = 'Justus Adam'
__version__ = '0.1'


class HtmlParserStack(object):
    __slots__ = (
        'element',
        'element_name',
        'argname',
        'kwarg_value',
        'text_content',
        'current'
    )

    def __init__(self,
        element = [],
        element_name = [],
        argname = [],
        kwarg_value = [],
        text_content = [],
        current = None
        ):
        self.element = element
        self.element_name = element_name
        self.argname = argname
        self.kwarg_value = kwarg_value
        self.text_content = text_content
        self.current = current

    def __bool__(self):
        return (bool(self.element) and bool(self.element_name) and
            bool(self.argname) and bool(self.kwarg_value)
            and bool(self.text_content))

    def __str__(self):
        return ('element: {}\nelement_name: {}\nargname: {}\nkwarg_value: {}'
            '\ntext_content: {}\ncurrent: {}'.format(self.element,
            self.element_name, self.argname, self.kwarg_value,
            self.text_content, self.current))


def flush_text_content(n, stack):
    if stack.text_content:
        if not (len(stack.text_content) == 1 and stack.text_content[0] == ' '):
            stack.current.content.append(''.join(stack.text_content))
        stack.text_content.clear()


def html_q2(n, stack):
    stack.element.append(stack.current)
    stack.current = html.elements[''.join(stack.element_name)]()
    stack.element_name.clear()


def html_q4(n, stack):
    current.params.add(''.join(stack.argname))
    stack.argname.clear()


def html_q6(n, stack):
    stack.current.value_params[''.join(stack.argname)] = ''.join(stack.kwarg_value)
    stack.argname.clear()
    stack.kwarg_value.clear()


def html_q11(n, stack):
    name = ''.join(stack.element_name)
    stack.element_name.clear()
    if stack.current.html_type != name:
        raise SyntaxError(
            'Mismatched closing tag. Expected {}, found {}'.format(
                stack.current.html_type, name))
    html_finish_element(n, stack)


def html_finish_element(n, stack):
    parent = stack.element.pop()
    parent.content.append(stack.current)
    stack.current = parent


html_forbidden = {'"'}


html_automaton_base = {
    0: (
        generic.Edge(1, chars='<', g=flush_text_content),
        generic.Edge(0, funcs=str.isalpha, g=lambda n, stack: stack.text_content.append(n)),
        generic.Edge(8, chars={' ', '\n'}, g=lambda n, stack: stack.text_content.append(' '))
    ),
    1: (
        generic.Edge(2, funcs=str.isalpha, g=lambda n, stack: stack.element_name.append(n)),
        generic.Edge(10, chars='/')
    ),
    2: (
        generic.Edge(2, funcs=str.isalpha, g=lambda n, stack: stack.element_name.append(n)),
        generic.Edge(0, chars='>', g=html_q2),
        generic.Edge(3, chars=' ', g=html_q2)
    ),
    3: (
        generic.Edge(0, chars='>'),
        generic.Edge(4, funcs=str.isalpha, g=lambda n, stack: stack.argname.append(n)),
        generic.Edge(9, chars='/')
    ),
    4: (
        generic.Edge(3, chars=' ', g=html_q4),
        generic.Edge(4, funcs=str.isalpha, g=lambda n, stack: stack.argname.append(n)),
        generic.Edge(5, chars='=')
    ),
    5: (
        generic.Edge(6, chars='"'),
    ),
    6: (
        generic.Edge(6, funcs=lambda n: n not in html_forbidden,
            g=lambda n, stack: stack.kwarg_value.append(n)),
        generic.Edge(7, chars='"', g=html_q6)
    ),
    7: (
        generic.Edge(0, chars='>'),
        generic.Edge(3, chars=' ')
    ),
    8: (
        generic.Edge(8, chars={'\n', ' '}),
        generic.Edge(0, funcs=str.isalpha, g=lambda n, stack: stack.text_content.append(n)),
        generic.Edge(1, chars='<', g=flush_text_content)
    ),
    9: (
        generic.Edge(0, chars='>', g=html_finish_element),
    ),
    10: (
        generic.Edge(11, funcs=str.isalpha, g=lambda n, stack: stack.element_name.append(n)),
    ),
    11: (
        generic.Edge(0, chars='>', g=html_q11),
        generic.Edge(11, funcs=str.isalpha, g=lambda n, stack: stack.element_name.append(n))
    )
}

html_automaton = generic.automaton_from_dict(html_automaton_base)


def parse(string):
    cellar_bottom = html.ContainerElement()
    stack = HtmlParserStack(element=[cellar_bottom], current=cellar_bottom)
    stack = generic.parse(html_automaton, stack, string)
    if stack.current is not cellar_bottom:
        raise SyntaxError()
    else:
        return cellar_bottom.content
