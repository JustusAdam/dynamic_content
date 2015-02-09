import functools
import pathlib
from framework import dchp
from framework.http import response
from framework.util import config, structures
from framework import mvc
from dycm import theming, commons

__author__ = 'Justus Adam'
__version__ = '0.2'


def compile_nodes(res, dc_obj):

    @functools.lru_cache()
    def _get_template(_type):
        if ('theme_config' in dc_obj.config
            and dc_obj.config['theme_config'] is not None
            and _type in dc_obj.config['theme_config']):
            r = dc_obj.config['theme_config']['path'] + '/' + dc_obj.config['theme_config'][_type]
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
            dc_obj.context['title'] = res['title']
        template = _get_template('single_node_template')
        content = dchp.evaluator.evaluate_html(template, res)
    elif hasattr(res, '__iter__'):
        # try to find if object carries a title
        if hasattr(res, 'title'):
            dc_obj.context['title'] = res.title
        elif hasattr(res, '__getitem__') and 'title' in res:
            dc_obj.context['title'] = res['title']
        else:
            dc_obj.context['title'] = 'Overview'

        template = _get_template('multi_node_template')
        content = structures.InvisibleList(
            (dchp.evaluator.evaluate_html(template, a) for a in res)
            )
    elif isinstance(res, response.Response):
        return res
    else:
        raise AttributeError

    dc_obj.context['content'] = content
    return 'page'



def make_node(*, theme='default_theme'):
    @mvc.context.apply_to_context(apply_before=False, with_return=True, return_from_decorator=True)
    def _inner(dc_obj, res):
        dc_obj.config['theme'] = theme
        theming.theme_dc_obj(dc_obj)
        commons.add_regions(dc_obj)
        theming.attach_breadcrumbs(dc_obj)
        return compile_nodes(res, dc_obj)
    return _inner
