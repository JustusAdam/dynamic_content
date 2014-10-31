__author__ = 'justusadam'



class Model(dict):
    __final = False
    decorator_attributes = set()

    def __init__(self, name, **kwargs):
        super().__init__(**kwargs)
        self.view = name

    def __setitem__(self, key, value):
        if self.__final:
            return
        dict.__setitem__(self, key, value)

    def assign_key_safe(self, key, value):
        if key in self and self[key]:
            print('key ' + key + ' already exists in template')
        else:
            self.__setitem__(key, value)

    def finalize(self):
        self.__final = True