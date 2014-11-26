from dynct.core.mvc.controller import controller_mapper
from dynct.core.mvc.decorator import controller_function, controller_class, controller_method
from dynct.core.mvc.model import Model
from dynct.util.url import Url

__author__ = 'justusadam'


@controller_function('hello')
def handle(*args, **kwargs):
    print('okay')


@controller_class
class test:

    @controller_method('lala')
    def some(self, *args, **kwargs):
        print(self)
        print('okay as well')


print(controller_mapper)
print(controller_mapper._controller_classes)

controller_mapper(Model() , Url('/hello'))
controller_mapper(Model() , Url('/lala'))