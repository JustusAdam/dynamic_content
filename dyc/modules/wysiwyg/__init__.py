from dyc.core.mvc import context as _context
from dyc.util import html, decorators
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
        model['scripts'] = [basic_script, apply_script]


def use(name='tinymce'):
    @decorators.apply_to_type(_context.Context, apply_before=False)
    def _inner(model):
        decorator_hook(model)
    return _inner