from dyc.util import html
import functools


__author__ = 'justusadam'
__version__ = '0.1'


class ParserStack(object):
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


def parse(page):
    stack = ParserStack()

    cellar_bottom = html.ContainerElement()
    stack.element.append(cellar_bottom)
    stack.current = cellar_bottom

    funcs = {
        0: q0,
        1: q1,
        2: q2,
        3: q3,
        4: q4,
        5: q5,
        6: q6,
        7: q7,
        8: q8,
        9: q9,
        10: q10
    }

    next = 0

    for n in page:
        try:
            next = funcs[next](n, stack)
        except:
            print(stack)
            return None

    if stack.current is not cellar_bottom or stack:
        raise SyntaxError()
    return cellar_bottom.content

def q0(n, stack):
    if n == '<':
        if stack.text_content:
            stack.current.content.append(''.join(stack.text_content))
            stack.text_content.clear()
        return 1
    elif n == ' ':
        stack.text_content.append(n)
        return 8
    elif n == '\n':
        return 0
    elif n.isalpha():
        stack.text_content.append(n)
        return 0
    else:
        raise SyntaxError('Expected "<" or text, got {}'.format(n))

def q1(n, stack):
    if n == '/':
        return 9
    elif n.isalpha():
        stack.element_name.append(n)
        return 2
    else:
        raise SyntaxError('Expected name, got {}'.format(n))

def q2(n, stack):
    if n == ' ' or n == '>':
        stack.element.append(stack.current)
        stack.current = html.elements[''.join(stack.element_name)]()
        stack.element_name.clear()
        return 0 if n == '>' else 3
    elif n.isalpha():
        stack.element_name.append(n)
        return 2

def q3(n, stack):
    if n == ' ':
        return 3
    elif n == '>':
        return 0
    elif n == '/':
        return 10
    elif n.isalpha():
        stack.argname.append(n)
        return 4
    else:
        raise SyntaxError('Expected ">" or argument name, got {}'.format(n))

def q4(n, stack):
    if n == ' ' or n == '>':
        current.params.add(''.join(stack.argname))
        stack.argname.clear()
        return 3 if n == ' ' else 0
    elif n == '=':
        return 5
    elif n.isalpha():
        stack.argname.append(n)
        return 4
    else:
        raise SyntaxError('Expected ">", " " or name continuation, got {}'.format(n))

def q5(n, stack):
    if n == '"':
        return 6
    else:
        raise SyntaxError('Expected \'"\', got {}'.format(n))

def q6(n, stack):
    if n == '"':
        stack.current.value_params[''.join(stack.argname)] = ''.join(stack.kwarg_value)
        stack.argname.clear()
        stack.kwarg_value.clear()
        return 7
    else:
        stack.kwarg_value.append(n)
        return 6

def q7(n, stack):
    if n == ' ':
        return 3
    elif n == '>':
        return 0
    else:
        raise SyntaxError('Expected " ", or ">", got {}'.format(n))

def q8(n, stack):
    if n == ' ' or n == '\n':
        return 8
    elif n == '<':
        return 1
    else:
        stack.text_content.append(n)
        return 0

def q9(n, stack):
    if n.isalpha():
        stack.element_name.append(n)
        return 10
    else:
        raise SyntaxError('Expected element name')

def q10(n, stack):
    if n == '>':
        name = ''.join(stack.element_name)
        stack.element_name.clear()
        if name != stack.current.html_type:
            raise SyntaxError('Expected closing tag for element {}, got {}'.format(stack.current.html_type, name))
        parent = stack.element.pop()
        parent.content.append(stack.current)
        stack.current = parent
        return 0
    elif n.isalpha():
        stack.element_name.append(n)
        return 10
