from dyc.util import html

__author__ = 'justusadam'

identifier = 'wysiwyg'


class WysiwygTextarea(html.Textarea):
    def __init__(self, *content, classes:set=None, name:str=None, form:str=None, required=False,
                 rows=0, cols=0, additional:dict=None):
        super().__init__(*content, classes=classes, element_id=identifier, name=name, form=form, required=required,
                         rows=rows, cols=cols, additional=additional)