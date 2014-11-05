from dynct.modules.comp.html_elements import Textarea, Script

__author__ = 'justusadam'


identifier = 'wysiwyg'

class WysiwygTextarea(Textarea):
    def __init__(self, *content, classes:set=None, name:str=None, form:str=None, required=False,
                 rows=0, cols=0, additionals:dict=None):
        super().__init__(*content, classes=classes, element_id=identifier, name=name, form=form, required=required,
                         rows=rows, cols=cols, additionals=additionals)