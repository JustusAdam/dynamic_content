from dynct import core
from dynct.modules.comp import html
from dynct.modules.iris import model as _model

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