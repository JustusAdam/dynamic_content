from . import model, base
from . import component

__author__ = 'Justus Adam'


@component.implements('com_text')
class TextCommons(base.Handler):
    type = 'text'

    def get_content(self, conf, render_args, client):
        return model.CommonData.get(model.CommonData.machine_name == conf.machine_name).content