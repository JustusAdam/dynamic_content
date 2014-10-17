import re

__author__ = 'justusadam'

VAR_REGEX = re.compile("\{([\w_-]*?)\}")


class Template(dict):
    def __init__(self, template_path, **kwargs):
        super().__init__(**kwargs)
        self._template = open(template_path).read()
        for a in VAR_REGEX.finditer(self._template):
            if a.group(1) not in self:
                dict.__setitem__(self, a.group(1), '')

    def template(self):
        return self._template

    def __setitem__(self, key, value):
        if key not in self:
            print('trying to assign to non existent key: ' + key)
        dict.__setitem__(self, key, value)

    def assign_key_safe(self, key, value):
        if self[key]:
            print('key ' + key + ' already exists in template')
        else:
            self.__setitem__(key, value)


    @property
    def compiled(self):
        return self._template.format(**self)

    def __str__(self):
        return self.compiled