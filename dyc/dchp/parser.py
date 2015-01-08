from dyc.util.parser import html, generic, elements


__author__ = 'Justus Adam'
__version__ = '0.1'


class ParserStack(html.ParserStack):
    __slots__ = (
        'element',
        'element_name',
        'argname',
        'kwarg_value',
        'text_content',
        'current',
        'dchp_content',
        'dchp_element_name',
        'dchp_indent',
        'dchp_active_indent'
    )

    def __init__(self,
        element = [],
        element_name = [],
        argname = [],
        kwarg_value = [],
        text_content = [],
        current = None,
        dchp_content = [],
        dchp_element_name = [],
        dchp_indent = 0,
        dchp_active_indent = 0
        ):
        super().__init__(
            element=element,
            element_name=element_name,
            argname=argname,
            kwarg_value=kwarg_value,
            text_content=text_content,
            current=current
        )
        self.dchp_content = dchp_content
        self.dchp_element_name = dchp_element_name
        self.dchp_indent = dchp_indent
        self.dchp_active_indent = dchp_active_indent


class DcHPElement(elements.Base):
    def __init__(self, code):
        super().__init__('dchp')
        self.code = code
        self.executed = None

    def render(self):
        if self.executed is None:
            return super().render()
        else:
            return str(self.executed)
            

html_base = html.automaton_base


def q30(n, stack):
    name = ''.join(stack.dchp_element_name)
    if name != 'dchp':
        raise SyntaxError('Expected name "dchp", found "{}"'.format(name))
    stack.dchp_element_name.clear()
    stack.dchp_indent = 0


def append_char(n, stack):
    stack.dchp_content.append(n)


def q44(n, stack):
    stack.dchp_content.append('?')
    stack.dchp_content.append(n)


def finalize(n, stack):
    stack.current.append(DcHPElement(''.join(stack.dchp_content)))
    stack.dchp_content.clear()


def increment_indent(n, stack):
    stack.dchp_indent += 1


def reset_indent(n, stack):
    stack.dchp_indent = 0


def reduce_indent(n, stack):
    if stack.dchp_indent == 0:
        stack.dchp_content.append(n)
        return 42
    if n != ' ':
        raise SyntaxError('Expected Indent of {}, found {}'.format(
            stack.dchp_indent, stack.dchp_indent - stack.dchp_active_indent))
    if stack.dchp_active_indent == 1:
        return 42
    stack.dchp_active_indent -= 1


def reset_active_indent(n, stack):
    stack.dchp_content.append(n)
    stack.dchp_active_indent = stack.dchp_indent


def q47(n, stack):
    if stack.dchp_active_indent <= 1:
        return 44
    else:
        return 48


automaton_base = (
    generic.Edge(30, 1, chars='?'),

    generic.Edge(31, 30, funcs=str.isalnum,
        g=lambda n, stack: stack.dchp_element_name.append(n)),

    generic.Edge(31, 31, funcs=str.isalnum,
        g=lambda n, stack: stack.dchp_element_name.append(n)),
    generic.Edge(41, 31, chars={' ', '\n'}, g=q30),
    generic.Edge(48, 31, chars='?', g=q30),

    generic.Edge(41, 41, chars={' '}, g=increment_indent),
    generic.Edge(41, 41, chars={'\n'}, g=reset_indent),
    generic.Edge(42, 41, funcs=lambda a: True,
        g=lambda n, stack: stack.dchp_content.append(n)),
    generic.Edge(45, 41, chars='\'', g=append_char),
    generic.Edge(46, 41, chars='"', g=append_char),
    generic.Edge(44, 41, chars='?'),

    generic.Edge(42, 42, funcs=lambda a: True, g=append_char),
    # generic.Edge(43, 42, chars=' ', g=append_char),
    generic.Edge(47, 42, chars='\n', g=reset_active_indent),
    generic.Edge(45, 42, chars='\'', g=append_char),
    generic.Edge(46, 42, chars='"', g=append_char),
    generic.Edge(44, 42, chars='?'),

    # generic.Edge(42, 43, funcs=lambda a: True, g=append_char),
    # generic.Edge(45, 43, chars='\'', g=append_char),
    # generic.Edge(46, 43, chars='"', g=append_char),
    # generic.Edge(44, 43, chars='?'),
    # generic.Edge(47, 43, chars='\n', g=reset_active_indent),

    generic.Edge(0, 44, chars='>', g=finalize),
    generic.Edge(42, 44, funcs=lambda a: True, g=q44),
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
    cellar_bottom = elements.by_name('cellar')
    stack = ParserStack(element=[cellar_bottom], current=cellar_bottom)
    stack = generic.parse(automaton, stack, string)
    if stack.current is not cellar_bottom:
        raise SyntaxError()
    else:
        return cellar_bottom.content()
