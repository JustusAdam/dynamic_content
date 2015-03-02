import html as _html


__author__ = 'Justus Adam'
__version__ = '0.1'


def to_html_head(*items):
    return ' '.join(_to_html_head(a) for a in items if a)


def _to_html_head(item):
    return _head_render_map.get(type(item), _str_to_html_head)(item)


def _dict_to_html_head(dict_):
    return ' '.join(_to_html_head(k) + '="' + _to_html_head(v) + '"' for k, v in dict_.items() if v)


def _iterable_to_html_head(list_):
    return ' '.join(_to_html_head(a) for a in list_ if a)

def _str_to_html_head(elem):
    return _html.escape(str(elem))


_head_render_map = {
    dict: _dict_to_html_head,
    list: _iterable_to_html_head,
    tuple: _iterable_to_html_head,
    int: str,
    float: str,
    set: _iterable_to_html_head,
    str: _str_to_html_head
}
