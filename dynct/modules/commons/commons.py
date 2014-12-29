from . import model, base

__author__ = 'justusadam'


class TextCommons(base.Commons):
    com_type = 'text'

    def get_content(self, name):
        return model.CommonData.get(model.CommonData.machine_name == name).content