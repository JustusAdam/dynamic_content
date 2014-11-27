from pathlib import Path
from dynct.core.mvc.model import Model
from dynct.modules.iris.node import Node
from dynct.util.config import read_config
from dynct.util.decorators import apply_to_type

__author__ = 'justusadam'


@apply_to_type(Model, apply_in_decorator=True)
def node_process(func):
    def wrap(model):

        # get node(s)
        res = func()
        if isinstance(res, Node):
            # assign title, if it exists
            if 'title' in res:
                model['title'] = res['title']
            with open(_template('single_node_template')) as template:
                content =  template.read().format(**res)
        elif hasattr(res, '__iter__'):
            # try to find if object carries a title
            if hasattr(res, 'title'): model['title'] = res.title
            elif hasattr(res, '__getitem__') and 'title' in res: model['title'] = res['title']
            else: model['title'] = 'Overview'

            with open(_template('multi_node_template')) as template:
                template = template.read()
                return ''.join([template.format(**a) for a in res])
        else:
            raise AttributeError
        model['content'] = content
        return 'page'

    def _template(_type):
        r = read_config(Path(__file__).parent / 'config')[_type]
        r = r if r.endswith('.html') else r + '.html'
        return str(Path(__file__).parent / r)

    return wrap