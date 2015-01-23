from dyc.modules.theming import InvisibleList
from dyc.util import html, structures
from ._elements import WysiwygTextarea, identifier
from dyc.core.mvc import context

__author__ = 'Justus Adam'

basic_script = html.Script(src='/public/tinymce/tinymce.min.js')

apply_script = html.Script(
    'tinymce.init({selector: "textarea.' + identifier + '"});'
)


def decorator_hook(dc_obj:structures.DynamicContent):
    if 'scripts' in dc_obj.context:
        dc_obj.context['scripts'] += [basic_script, apply_script]
    else:
        dc_obj.context['scripts'] = InvisibleList((basic_script, apply_script))


def use(name='tinymce'):
    @context.apply_to_context(apply_before=False)
    def _inner(model):
        decorator_hook(model)
    return _inner
