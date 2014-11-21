from dynct.util.config import read_config

__author__ = 'justusadam'


class Node(dict):
    pass


class NodeProcess:
    def __init__(self, func):
        self.function = func

    def __call__(self, other, model, *args, **kwargs):
        res = self.function(other, model, *args, **kwargs)
        if hasattr(res, '__iter__'):
            content = self._process_nodes(res)
        else:
            content = self._process_single_node(res)
        model['content'] = content

    def _process_single_node(self, node):
        return open(self._template('single_node_template')).read().format(**node)

    def _process_nodes(self, nodes):
        template = open(self._template('multi_node_template')).read()
        return ''.join([template.format(**a) for a in nodes])

    def _template(self, _type):
        return read_config('config')[_type]