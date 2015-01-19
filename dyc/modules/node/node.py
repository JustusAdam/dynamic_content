import pathlib
from dyc.core.mvc.context import apply_to_context
from dyc.modules import theming
from dyc.modules import commons
from dyc.util import config, decorators
from dyc import dchp


__author__ = 'Justus Adam'
__version__ = '0.2'


class InvisibleList(list):
    def __str__(self):
        return ''.join(str(a) for a in self)


def compile_nodes(res, model):

    @decorators.multicache
    def _get_template(_type):
        if (hasattr(model, 'theme_config')
            and model.theme_config is not None
            and _type in model.theme_config):
            r = model.theme_config[_type]
        else:
            r = config.read_config(pathlib.Path(__file__).parent / 'config')[_type]
        r = r if r.endswith('.html') else r + '.html'
        path = str(pathlib.Path(__file__).parent / r)

        with open(path) as template:
            return template.read()


    if isinstance(res, dict):
        # assign title, if it exists
        if 'title' in res:
            model['title'] = res['title']
        template = _get_template('single_node_template')
        content = dchp.evaluator.evaluate_html(template, res)
    elif hasattr(res, '__iter__'):
        # try to find if object carries a title
        if hasattr(res, 'title'):
            model['title'] = res.title
        elif hasattr(res, '__getitem__') and 'title' in res:
            model['title'] = res['title']
        else:
            model['title'] = 'Overview'

        template = _get_template('multi_node_template')
        content = InvisibleList(
            dchp.evaluator.evaluate_html(template, a) for a in res
            )
    else:
        raise AttributeError

    model['content'] = content
    return 'page'


@apply_to_context(apply_before=False, with_return=True, return_from_decorator=True)
def node(context, res):
    theming.theme_model(context)
    commons.add_regions(context)
    theming.attach_breadcrumbs(context)
    return compile_nodes(res, context)