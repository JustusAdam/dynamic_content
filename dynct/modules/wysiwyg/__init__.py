from dynct.core.mvc.model import Model
from dynct.modules.comp.html_elements import Script, ContainerElement
from ._elements import identifier, WysiwygTextarea

__author__ = 'justusadam'


def init(model:Model):
    from . import _elements
    model.decorator_attributes.add('include module wysiwyg')
    return _elements


def decorator_hook(model:Model):
    if 'scripts' in model:
        model['scripts'] += [Script('/public/tinymce/js/tinymce.min.js'), ContainerElement(
            'tinymce.init({selector: "textarea#' + identifier + '"});',
            html_type='script', additionals={'type': 'text/javascript'}
        )]
    else:
        model['scripts'] = [Script('/public/tinymce/js/tinymce.min.js')]