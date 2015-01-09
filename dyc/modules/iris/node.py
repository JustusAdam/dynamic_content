import pathlib
from dyc.core.mvc import model as mvc_model
from dyc.util import config, decorators

__author__ = 'Justus Adam'


class Node(dict):
    pass


@decorators.multicache
def _get_template(_type):
    r = config.read_config(pathlib.Path(__file__).parent / 'config')[_type]
    r = r if r.endswith('.html') else r + '.html'
    path = str(pathlib.Path(__file__).parent / r)

    with open(path) as template:
        return template.read()



@decorators.apply_to_type(mvc_model.Model, apply_in_decorator=True)
def node_process(func):
    def wrap(model):

        # get node(s)
        res = func()
        if isinstance(res, Node):
            # assign title, if it exists
            if 'title' in res:
                model['title'] = res['title']
            temlpate = _get_template('single_node_template')
            content = template.format(**res)
        elif hasattr(res, '__iter__'):
            # try to find if object carries a title
            if hasattr(res, 'title'):
                model['title'] = res.title
            elif hasattr(res, '__getitem__') and 'title' in res:
                model['title'] = res['title']
            else:
                model['title'] = 'Overview'

            template = _get_template('multi_node_template')
            content = ''.join([template.format(**a) for a in res])
        else:
            raise AttributeError
        model['content'] = content
        return 'page'

    def _template(_type):


    return wrap
