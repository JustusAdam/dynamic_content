import unittest

from dynct.core.mvc.controller import url_args
from dynct.util.url import Url

__author__ = 'justusadam'

url = Url('/klk/?gg=hello', {'lala': 'jhjhjh'})
args = ('.*', )
kwargs = dict(get=['gg'], post=True)

def wrap1(func):
    def wrap(model):
        model.test1 = "test1 works"
        return func(model)
    return wrap


def wrap2(func):
    def wrap(model):
        model.test2 = "test2 works"
        return func(model)
    return wrap


class Test(unittest.TestCase):


    def method(self, gg, client, post):
        print(gg)
        print(post)

    def test_regex(self):


        def test(gg, client, post):
            print(gg)
            print(post)

    def test_mult_dec(self):
        class Someclass:
            pass

        m = Someclass()

        @wrap1
        @wrap2
        def p(model):
            print(model.test1, model.test2)
        p(m)