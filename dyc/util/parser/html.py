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


html_automaton_base = (
    generic.Edge(1, 0, chars='<', g=flush_text_content),
    generic.Edge(0, 0, funcs=str.isalpha, g=lambda n, stack: stack.text_content.append(n)),
    generic.Edge(8, 0, chars={' ', '\n'}, g=lambda n, stack: stack.text_content.append(' ')),
    generic.Edge(2, 1, funcs=str.isalpha, g=lambda n, stack: stack.element_name.append(n)),
    generic.Edge(10, 1, chars='/'),
    generic.Edge(2, 2, funcs=str.isalpha, g=lambda n, stack: stack.element_name.append(n)),
    generic.Edge(0, 2, chars='>', g=html_q2),
    generic.Edge(3, 2, chars=' ', g=html_q2),
    generic.Edge(0, 3, chars='>'),
    generic.Edge(4, 3, funcs=str.isalpha, g=lambda n, stack: stack.argname.append(n)),
    generic.Edge(9, 3, chars='/'),
    generic.Edge(3, 4, chars=' ', g=html_q4),
    generic.Edge(4, 4, funcs=str.isalpha, g=lambda n, stack: stack.argname.append(n)),
    generic.Edge(5, 4, chars='='),
    generic.Edge(6, 5, chars='"'),
    generic.Edge(6, 6, funcs=lambda n: n not in html_forbidden,
        g=lambda n, stack: stack.kwarg_value.append(n)),
    generic.Edge(7, 6, chars='"', g=html_q6),
    generic.Edge(0, 7, chars='>'),
    generic.Edge(3, 7, chars=' '),
    generic.Edge(8, 8, chars={'\n', ' '}),
    generic.Edge(0, 8, funcs=str.isalpha, g=lambda n, stack: stack.text_content.append(n)),
    generic.Edge(1, 8, chars='<', g=flush_text_content),
    generic.Edge(0, 9, chars='>', g=html_finish_element),
    generic.Edge(11, 10, funcs=str.isalpha, g=lambda n, stack: stack.element_name.append(n)),
    generic.Edge(0, 11, chars='>', g=html_q11),
    generic.Edge(11, 11, funcs=str.isalpha, g=lambda n, stack: stack.element_name.append(n))
)

html_automaton = generic.automaton_from_list(html_automaton_base)


def parse(string):
    cellar_bottom = html.ContainerElement()
    stack = HtmlParserStack(element=[cellar_bottom], current=cellar_bottom)
    stack = generic.parse(html_automaton, stack, string)
    if stack.current is not cellar_bottom:
        raise SyntaxError()
    else:
        return cellar_bottom.content
