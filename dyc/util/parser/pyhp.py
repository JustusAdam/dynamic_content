from . import html, generic
from .. import html as _html


class ParserStack(html.ParserStack):
    __slots__ = (
        'element',
        'element_name',
        'argname',
        'kwarg_value',
        'text_content',
        'current',
        'pyhp_content',
        'pyhp_element_name'
    )

    def __init__(self,
        element = [],
        element_name = [],
        argname = [],
        kwarg_value = [],
        text_content = [],
        current = None,
        pyhp_content = [],
        pyhp_element_name = []
        ):
        super().__init__(
            element=element,
            element_name=element_name,
            argname=argname,
            kwarg_value=kwarg_value,
            text_content=text_content,
            current=current
        )
        self.pyhp_content = pyhp_content
        self.pyhp_element_name = pyhp_element_name


class PyHPElement(object):
    def __init__(self, code):
        self.code = code


html_base = html.automaton_base


def q30(n, stack):
    name = ''.join(stack.pyhp_element_name)
    if name != 'pyhp':
        raise SyntaxError()
    stack.pyhp_element_name.clear()


def append_char(n, stack):
    stack.pyhp_content.append(n)


def q44(n, stack):
    stack.pyhp_content.append('?')
    stack.pyhp_content.append(n)


def finalize(n, stack):
    stack.current.content.append(PyHPElement(''.join(stack.pyhp_content)))
    stack.pyhp_content.clear()


automaton_base = (
    generic.Edge(30, 1, chars='?'),
    generic.Edge(31, 30, funcs=str.isalpha,
        g=lambda n, stack: stack.pyhp_element_name.append(n)),
    generic.Edge(31, 31, funcs=str.isalpha,
        g=lambda n, stack: stack.pyhp_element_name.append(n)),
    generic.Edge(42, 31, chars=' ', g=q30),
    generic.Edge(42, 42, funcs=lambda a: True, g=append_char),
    generic.Edge(43, 42, chars={' ', '\n'}, g=append_char),
    generic.Edge(45, 42, chars='\'', g=append_char),
    generic.Edge(46, 42, chars='"', g=append_char),
    generic.Edge(42, 43, funcs=lambda a: True, g=append_char),
    generic.Edge(45, 43, chars='\'', g=append_char),
    generic.Edge(46, 43, chars='"', g=append_char),
    generic.Edge(44, 43, chars='?'),
    generic.Edge(0, 44, chars='>', g=finalize),
    generic.Edge(42, 44, funcs=lambda a: True),
    generic.Edge(45, 44, chars='\'', g=q44),
    generic.Edge(46, 44, chars='"', g=q44),
    generic.Edge(42, 45, chars='\'', g=append_char),
    generic.Edge(45, 45, funcs=lambda a: True, g=append_char),
    generic.Edge(42, 46, chars='"', g=append_char),
    generic.Edge(46, 46, funcs=lambda a: True, g=append_char)
)


automaton = generic.automaton_from_list(html.automaton_base + automaton_base)


def parse(string):
    cellar_bottom = _html.ContainerElement()
    stack = ParserStack(element=[cellar_bottom], current=cellar_bottom)
    stack = generic.parse(automaton, stack, string)
    if stack.current is not cellar_bottom:
        raise SyntaxError()
    else:
        return cellar_bottom.content
