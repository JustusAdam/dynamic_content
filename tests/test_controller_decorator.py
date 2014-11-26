from dynct.core.mvc.controller import controller_mapper
from dynct.core.mvc.decorator import controller

__author__ = 'justusadam'


@controller('hello')
def handle():
    pass

class test():

    @controller('')
    def some(self):
        pass


print(controller_mapper)

test().some()