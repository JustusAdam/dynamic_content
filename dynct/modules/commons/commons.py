from .base import Commons
from . import model

__author__ = 'justusadam'


class TextCommons(Commons):
    com_type = 'text'

    def get_content(self, name):
        return model.com(self.com_type).get(machine_name=name).content