from pathlib import Path
from dynct.core.mvc.model import Model
from dynct.util.config import read_config
from dynct.util.decorators import apply_to_type

__author__ = 'justusadam'


@apply_to_type(Model, apply_in_decorator=True)
def node_process(func):
    def wrap(model):
        res = func()
        if hasattr(res, '__iter__'):
            content = _process_nodes(res)
        else:
            content = _process_single_node(res)
        model['content'] = content
        return 'page'

    def _process_single_node(node):
        with open(_template('single_node_template')) as template:
            return template.read().format(**node)

    def _process_nodes(nodes):
        with open(_template('multi_node_template')) as template:
            template = template.read()
            return ''.join([template.format(**a) for a in nodes])

    def _template(_type):
        r = read_config(Path(__file__).parent / 'config')[_type]
        r = r if r.endswith('.html') else r + '.html'
        return str(Path(__file__).parent / r)

    return wrap