from dyc.util.parser import html, generic
from dyc.util import html as _html


class ParserStack(html.ParserStack):
    __slots__ = (
        'element',
        'element_name',
        'argname',
        'kwarg_value',
        'text_content',
        'current',
        'pyhp_content',
        'pyhp_element_name',
        'pyhp_indent',
        'pyhp_active_indent'
    )

    def __init__(self,
        element = [],
        element_name = [],
        argname = [],
        kwarg_value = [],
        text_content = [],
        current = None,
        pyhp_content = [],
        pyhp_element_name = [],
        pyhp_indent = 0,
        pyhp_active_indent = 0
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
        self.pyhp_indent = pyhp_indent
        self.pyhp_active_indent = pyhp_active_indent


class PyHPElement(_html.BaseElement):
    def __init__(self, code):
        super().__init__('pyhp')
        self.code = code
        self.executed = None

    def __str__(self):
        if self.executed:
            return self.executed
        else:
            return super().__str__()


html_base = html.automaton_base


def q30(n, stack):
    name = ''.join(stack.pyhp_element_name)
    if name != 'pyhp':
        raise SyntaxError()
    stack.pyhp_element_name.clear()
    stack.pyhp_indent = 0


def append_char(n, stack):
    stack.pyhp_content.append(n)


def q44(n, stack):
    stack.pyhp_content.append('?')
    stack.pyhp_content.append(n)


def finalize(n, stack):
    stack.current.content.append(PyHPElement(''.join(stack.pyhp_content)))
    stack.pyhp_content.clear()


def increment_indent(n, stack):
    stack.pyhp_indent += 1


def reset_indent(n, stack):
    stack.pyhp_indent = 0


def reduce_indent(n, stack):
    if stack.pyhp_indent == 0:
        stack.pyhp_content.append(n)
        return 42
    if n != ' ':
        raise SyntaxError('Expected Indent of {}, found {}'.format(
            stack.pyhp_indent, stack.pyhp_indent - stack.pyhp_active_indent))
    if stack.pyhp_active_indent == 1:
        return 42
    stack.pyhp_active_indent -= 1


def reset_active_indent(n, stack):
    stack.pyhp_content.append(n)
    stack.pyhp_active_indent = stack.pyhp_indent


def q47(n, stack):
    if stack.pyhp_active_indent <= 1:
        return 44
    else:
        return 48


automaton_base = (
    generic.Edge(30, 1, chars='?'),

    generic.Edge(31, 30, funcs=str.isalpha,
        g=lambda n, stack: stack.pyhp_element_name.append(n)),

    generic.Edge(31, 31, funcs=str.isalpha,
        g=lambda n, stack: stack.pyhp_element_name.append(n)),
    generic.Edge(41, 31, chars={' ', '\n'}, g=q30),

    generic.Edge(41, 41, chars={' '}, g=increment_indent),
    generic.Edge(41, 41, chars={'\n'}, g=reset_indent),
    generic.Edge(42, 41, funcs=lambda a: True,
        g=lambda n, stack: stack.pyhp_content.append(n)),
    generic.Edge(45, 41, chars='\'', g=append_char),
    generic.Edge(46, 41, chars='"', g=append_char),
    generic.Edge(44, 41, chars='?'),

    generic.Edge(42, 42, funcs=lambda a: True, g=append_char),
    generic.Edge(43, 42, chars=' ', g=append_char),
    generic.Edge(47, 42, chars='\n', g=reset_active_indent),
    generic.Edge(45, 42, chars='\'', g=append_char),
    generic.Edge(46, 42, chars='"', g=append_char),

    generic.Edge(42, 43, funcs=lambda a: True, g=append_char),
    generic.Edge(45, 43, chars='\'', g=append_char),
    generic.Edge(46, 43, chars='"', g=append_char),
    generic.Edge(44, 43, chars='?'),
    generic.Edge(47, 43, chars='\n', g=reset_active_indent),

    generic.Edge(0, 44, chars='>', g=finalize),
    generic.Edge(42, 44, funcs=lambda a: True),
    generic.Edge(45, 44, chars='\'', g=q44),
    generic.Edge(46, 44, chars='"', g=q44),
    generic.Edge(47, 44, chars='\n', g=reset_active_indent),

    generic.Edge(42, 45, chars='\'', g=append_char),
    generic.Edge(45, 45, funcs=lambda a: True, g=append_char),

    generic.Edge(42, 46, chars='"', g=append_char),
    generic.Edge(46, 46, funcs=lambda a: True, g=append_char),

    generic.Edge(47, 47, funcs=lambda a: True, g=reduce_indent),
    generic.Edge(47, 47, chars='\n', g=reset_active_indent),
    generic.Edge(48, 47, chars='?', g=q47),

    generic.Edge(0, 48, chars='>', g=finalize)
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
