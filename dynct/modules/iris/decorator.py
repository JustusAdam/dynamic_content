import pathlib
from dynct.core.mvc import model as mvc_model
from dynct.modules.iris import node
from dynct.util import config, decorators

__author__ = 'justusadam'


@decorators.apply_to_type(mvc_model.Model, apply_in_decorator=True)
def node_process(func):
    def wrap(model):

        # get node(s)
        res = func()
        if isinstance(res, node.Node):
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
                content = ''.join([template.format(**a) for a in res])
        else:
            raise AttributeError
        model['content'] = content
        return 'page'

    def _template(_type):
        r = config.read_config(pathlib.Path(__file__).parent / 'config')[_type]
        r = r if r.endswith('.html') else r + '.html'
        return str(pathlib.Path(__file__).parent / r)

    return wrap