from dyc.core.mvc import context as _context
from dyc.modules.theming import InvisibleList
from dyc.util import html
from ._elements import WysiwygTextarea, identifier

__author__ = 'Justus Adam'

basic_script = html.Script(src='/public/tinymce/tinymce.min.js')

apply_script = html.Script(
    'tinymce.init({selector: "textarea.' + identifier + '"});'
)


def decorator_hook(model:_context.Context):
    if 'scripts' in model:
        model['scripts'] += [basic_script, apply_script]
    else:
        model['scripts'] = InvisibleList((basic_script, apply_script))


def use(name='tinymce'):
    @_context.apply_to_context(apply_before=False)
    def _inner(model):
        decorator_hook(model)
    return _inner