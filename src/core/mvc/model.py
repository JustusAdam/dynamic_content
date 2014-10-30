__author__ = 'justusadam'


class Model(dict):
    __final = False
    decorator_attributes = []

    def __setitem__(self, key, value):
        if self.__final:
            return
        else:
            super().__setitem__(key, value)

    def finalize(self):
        self.__final = True