import collections
import functools


__author__ = 'Justus Adam'
__version__ = '0.1'


non_closing = {'meta', 'input'}


class Base(object):

    __slots__ = (
        '_children',
        '_value_params',
        '_params',
        'name'
    )

    def __init__(self, name, *children, **params):
        self.name = name
        self._children = list(children)
        self._params = set()
        self._value_params = dict()
        for k, v in params:
            if isinstance(v, bool):
                self._params.add(k)
            else:
                self._value_params[k] = v

    @property
    def value_params(self):
        return self._value_params

    @property
    def params(self):
        return self._params

    def __getattr__(self, k):
        if k in self._value_params:
            return self._value_params[k]
        else:
            return k in self._params

    def __setattr__(self, k, v):
        if k in self.__slots__:
            super().__setattr__(k, v)
        elif isinstance(v, bool):
            self._params.add(k)
        else:
            self._value_params[k] = v

    def children(self):
        return tuple(filter(lambda a: isinstance(a, Base), self._children))

    def text_fields(self):
        return tuple(filter(lambda a: isinstance(a, str), self._children))

    def text(self):
        return ''.join(self.text_fields())

    def render(self):
        def unwrap_list(l):
            if isinstance(l, str):
                return l
            elif hasattr(l, '__iter__'):
                return ', '.join(l)
            else:
                raise TypeError
        inner_head = ' '.join(
            (self.name, ) + tuple(self._params)
            + tuple(k + '="' + unwrap_list(v) + '"' for k,v in self._value_params.items() if v is not None)
            )
        if self._children:
            return ''.join(('<', inner_head, '>',
                ''.join(a if isinstance(a, str) else a.render() for a in self._children),
                '</', self.name,'>'))
        elif self.name in non_closing:
            return '<' + inner_head + '>'
        else:
            return '<' + inner_head + ' />'

    def __str__(self):
        return self.render()

    def append(self, child):
        self._children.append(child)

    def prepend(self, child):
        if not isinstance(self._children, collections.deque):
            self._children = collections.deque(self._children)

    def insert(self, index, element):
        self._children.insert(index, element)

    def content(self):
        return self._children

    def add_class(self, *classes):
        self._value_params.setdefault('class', set())
        for c in classes:
            self._value_params['class'].add(c)

    def _satisfies(self, *selectors, **vselectors):
        for selector in selectors:
            if not selector in self._params:
                return False
        for k, v in vselectors.items():
            if self._value_params[k] != v:
                return False
        return True


    def _find(self, *selectors, **vselectors):
        try:
            if self._satisfies(*selectors, **vselectors):
                yield self
        except KeyError:
            None
        for child in self.children():
            yield from child._find(*selectors, **vselectors)

    def find(self, *selectors, **vselectors):
        return tuple(self._find(*selector, **vselectors))


class _Hack(dict):
    def __getitem__(self, item):
        if item in self:
            return super().__getitem(item)
        else:
            return functools.partial(Base, item)


by_name = lambda name: Base(name)
