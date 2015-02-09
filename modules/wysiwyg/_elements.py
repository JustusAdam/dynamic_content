from dynamic_content.util import html

__author__ = 'Justus Adam'


identifier = 'wysiwyg'


class WysiwygTextarea(html.Textarea):
    def __init__(self, *content, classes:set=None, element_id=None, name:str=None, form:str=None, required=False,
                 rows=0, cols=0, additional:dict=None):
        super().__init__(*content, classes=classes, element_id=element_id, name=name, form=form, required=required,
                         rows=rows, cols=cols, additional=additional)
        self.classes.add(identifier)