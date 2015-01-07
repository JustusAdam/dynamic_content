import collections


__author__ = 'Justus Adam'
__version__ = '0.1'


class Edge(object):

    __slots__ = ('g', 'head', 'tail', 'chars', 'funcs')

    def __init__(self, head, tail, g=None, chars=set(), funcs=set()):
        self.head = head
        self.tail = tail
        self.g = g
        self.chars = {chars} if isinstance(chars, str) else set(chars)
        self.funcs = {funcs} if callable(funcs) else set(funcs)


EdgeFunc = collections.namedtuple('EdgeFunc', ('func', 'result'))


class Vertice(object):

    __slots__ = ('inner', 'f')

    def __init__(self, *edges):
        self.inner = {}
        self.f = set()
        for edge in edges:
            self.add_edge(edge)

    def add_edge(self, edge):
        for arg in edge.chars:
            if isinstance(arg, str):
                if arg in self.inner:
                    raise SyntaxError('Edge to {} already exists'.format(arg))
                self.inner[arg] = edge
            else:
                raise TypeError('Expected type {} or {}, got {}'.format(
                    str, callable, type(arg)))
        for f in edge.funcs:
            if callable(f):
                self.f.add(EdgeFunc(func=f, result=edge))
            else:
                raise TypeError('Expected type {} or {}, got {}'.format(
                    str, callable, type(arg)))

    def match(self, character):
        if character in self.inner:
            return self.inner[character]
        else:
            for f in self.f:
                if f.func(character):
                    return f.result


def _parse_deterministic(automaton, stack, string):

    linecount = 1
    charcount = 0

    node = automaton[0]

    for n in string:
        try:
            res = node.match(n)
            fres = res.g(n, stack) if res.g is not None else None
        except (KeyError, SyntaxError) as e:
            raise SyntaxError('On line {} column {}, nested exception {}'.format(
                linecount, charcount, e
            ))
        if res == None:
            raise SyntaxError('On line {} column: {} \nExpected character'
                'from {} or conforming to {}'.format(linecount,
                charcount, node.inner.keys(), set(f.func for f in node.f)))
        try:
            node = automaton[res.head if fres is None else fres]
        except KeyError:
            raise SyntaxError('No state {} found in Automaton'.format(res.head))

        if n == '\n':
            linecount += 1
            charcount = 0
        else:
            charcount += 1

    return stack


def _parse_indeterministic(automaton, stack, string):
    raise NotImplementedError


def automaton_from_list(l):
    sorter = collections.defaultdict(list)
    for item in l:
        sorter[item.tail].append(item)
    return {
        k: Vertice(*v) for k, v in sorter.items()
    }


def parse(automaton, stack, string, automaton_type='deterministic'):
    return {
        'deterministic': _parse_deterministic,
        'indeterministic': _parse_indeterministic
    }[automaton_type](automaton, stack, string)
