from dynct.core import Modules as _modules
from dynct.modules.comp.html import ContainerElement, List
from dynct.modules.iris import model

__author__ = 'justusadam'


_access_modifier = 'access'
_edit_modifier = 'edit'
_add_modifier = 'add'

_publishing_flag = 'published'

_step = 5

_scroll_left = '<'
_scroll_right = '>'


_editorial_list_base = {
    'access':[('edit', _edit_modifier)]
}



class Node(dict):
    pass



def access_node(model, node_type:str, node_id:int):
    page = get_page(node_type=node_type, node_id=node_id)
    fields = get_fields(content_type=page.content_type, node_type=node_type, node_id=node_id, modifier='access')
    return Node(
        content=process_content(fields),
        title=page.page_title,
        editorial=editorial_list(model.client, 'access', page.content_type, node_type, node_id)
    )


def get_page(node_type, node_id):
    return model.page(node_type).get(id=node_id)


def join_permission(modifier, content_type):
    return ' '.join([modifier, 'content type', content_type])


def get_fields(content_type, node_type, node_id, modifier):
    field_info = model.FieldConfig.get_all(content_type=content_type)
    for a in field_info:
        yield _modules[a.handler_module].field_handler(a.machine_name, node_type, node_id, modifier)


def handle_single_field_query(field_handler, query):
    query_keys = field_handler.get_post_query_keys()
    if query_keys:
        vals = {key:query.get(key, None) for key in query_keys if key in query_keys}
        if vals:
            field_handler.process_post(vals)


def concatenate_content(fields):
    content = field_content(fields)
    return ContainerElement(*content)


def field_content(fields):
    for field in fields:
        yield field.compile().content


def process_content(fields):
    return concatenate_content(fields)


def editorial_list(client, modifier, content_type, node_type, node_id):
    for (name, modifier) in _editorial_list_base[modifier]:
        if client.check_permission(join_permission(modifier, content_type)):
            yield name, '/'.join(['', node_type, str(node_id), modifier])


def editorial(client, modifier, content_type, node_type, node_id):
    l = editorial_list(client, modifier, content_type, node_type, node_id)
    if l:
        return List(
            *[ContainerElement(name, html_type='a', classes={'editorial-link'}, additional={'href': link}) for
              name, link in l],
            classes={'editorial-list'}
        )
    return ''