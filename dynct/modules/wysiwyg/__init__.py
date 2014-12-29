from dynct.core.mvc import model as _model
from dynct.modules.comp import html
from . import _elements
from ._elements import WysiwygTextarea

__author__ = 'justusadam'

basic_script = html.Script(src='/public/tinymce/tinymce.min.js')

apply_script = html.Script(
    'tinymce.init({selector: "textarea#' + _elements.identifier + '"});'
)


def init(model:_model.Model):
    from . import _elements

    model.decorator_attributes.add('include module wysiwyg')
    return _elements


def decorator_hook(model:_model.Model):
    if 'scripts' in model:
        model['scripts'] += [basic_script, apply_script]
    else:
        model['scripts'] = [basic_script, apply_script]