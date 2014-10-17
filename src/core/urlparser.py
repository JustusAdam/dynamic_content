import re

__author__ = 'justusadam'


class Parser(list):
    def __init__(self):
        super().__init__()

    def __setitem__(self, key, value):
        pass

    def register(self, pattern, callback):
        assert isinstance(pattern, str)
        compiled = re.compile(pattern)
        if pattern in self:
            raise ValueError
        self.append((compiled, callback))

    def parse(self, url):
        for (pattern, function) in self:
            if pattern.fullmatch(url):
                return function(url)
        raise ValueError