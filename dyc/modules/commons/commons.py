from . import model, base
from . import component

__author__ = 'justusadam'


# @component.implements('text')
class TextCommons(base.Commons):
    com_type = 'text'

    def get_content(self, name):
        return model.CommonData.get(model.CommonData.machine_name == name).content