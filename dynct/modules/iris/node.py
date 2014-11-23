from dynct.core import Modules
from dynct.core.ar import ContentTypes
from dynct.modules.iris import ar
from dynct.util.typesafe import typesafe

__author__ = 'justusadam'


_modules = Modules


class Node(dict):
    pass


class NodeAccessCompiler(object):
    @typesafe
    def __call__(self, node_type:str, node_id:int):
        pass

    @staticmethod
    def get_page(node_type, node_id):
        return ar.page(node_type).get(id=node_id)

    @staticmethod
    def join_permission(modifier, content_type):
        return ' '.join([modifier, 'content type', content_type])

    def get_fields(self, ):
        field_info = ar.FieldConfig.get_all(content_type=content_type)

        return [self.get_field_handler(a.machine_name, a.handler_module) for a in field_info]

    def handle_single_field_post(self, field_handler):
        query_keys = field_handler.get_post_query_keys()
        if query_keys:
            vals = {}
            for key in query_keys:
                if key in self.url.post:
                    vals[key] = self.url.post[key]
            if vals:
                field_handler.process_post(UrlQuery(vals))

    def handle_single_field_get(self, field_handler):
        query_keys = field_handler.get_post_query_keys()
        if query_keys:
            vals = {}
            for key in query_keys:
                if key in self.url.get_query:
                    vals[key] = self.url.post[key]
            if vals:
                field_handler.process_get(UrlQuery(vals))

    def get_field_handler(self, name, module):
        return self.modules[module].field_handler(name, self.url.page_type, self.url.page_id, self.modifier)

    def concatenate_content(self, fields):
        content = self.field_content(fields)
        return ContainerElement(*content)

    def field_content(self, fields):
        content = []
        for field in fields:
            content.append(field.compile().content)
        return content

    def process_content(self):
        return self.concatenate_content(self.fields)

    def editorial_list(self):
        s = []
        for (name, modifier) in self._editorial_list_base:
            if self.check_permission(self.join_permission(modifier, self.page.content_type)):
                s.append((name, '/'.join(['', self.url.page_type, str(self.url.page_id), modifier])))
        return s