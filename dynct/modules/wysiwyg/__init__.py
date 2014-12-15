from dynct.core.mvc.model import Model
from dynct.modules.comp.html import Script
from ._elements import identifier, WysiwygTextarea

__author__ = 'justusadam'

basic_script = Script(src='/public/tinymce/tinymce.min.js')

apply_script = Script(
        'tinymce.init({selector: "textarea#' + identifier + '"});'
    )


def init(model:Model):
    from . import _elements
    model.decorator_attributes.add('include module wysiwyg')
    return _elements


def decorator_hook(model:Model):
    if 'scripts' in model:
        model['scripts'] += [basic_script, apply_script]
    else:
        model['scripts'] = [basic_script, apply_script]