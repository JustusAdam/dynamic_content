import pathlib
from dyc import modules
from dyc import dchp
from dyc.dchttp import response
from dyc.util import config, decorators
from dyc.core import mvc
theming, commons = modules.import_modules('theming', 'commons')


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
            r = model.theme_config['path'] + '/' + model.theme_config[_type]
        else:
            basepath = pathlib.Path(__file__).parent
            r = config.read_config(basepath / 'config')[_type]
            r = str(basepath / r)

        r = r if r.endswith('.html') else r + '.html'
        path = str(pathlib.Path(r))

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
    elif isinstance(res, response.Response):
        return res
    else:
        raise AttributeError

    model['content'] = content
    return 'page'



def make_node(*, theme='default_theme'):
    @mvc.context.apply_to_context(apply_before=False, with_return=True, return_from_decorator=True)
    def _inner(context, res):
        context.theme = theme
        theming.theme_model(context)
        commons.add_regions(context)
        theming.attach_breadcrumbs(context)
        return compile_nodes(res, context)
    return _inner