import unittest

from dynct.core.mvc.controller import url_args
from dynct.util.url import Url

__author__ = 'justusadam'


class Test(unittest.TestCase):

    def test_regex(self):

        @url_args('.*', get=['gg'], post=True)
        def test(gg, client, post):
            print(gg)
            print(post)

        url = Url('/klk/?gg=hello', {'lala': 'jhjhjh'})

        test(url, None)