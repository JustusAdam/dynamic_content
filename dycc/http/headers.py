__author__ = 'Justus Adam'
__version__ = '0.1'


class Header:
    def __init__(self, key, value):
        self.key = key
        self.value = value

    def __str__(self):
        return self.key + '='