import html as _html

__author__ = 'justusadam'


def to_html_head(*items):
    return ' '.join([_to_html_head(a) for a in items if a])


def _to_html_head(item):
    return _head_render_map.get(type(item), lambda a: _html.escape(str(a)))(item)


def _dict_to_html_head(dict_):
    return ' '.join(_to_html_head(k) + '="' + _to_html_head(v) + '"' for k, v in dict_.items() if v)


def _list_to_html_head(list_):
    return ' '.join([_to_html_head(a) for a in list_ if a])


_head_render_map = {
    dict: _dict_to_html_head,
    list: _list_to_html_head,
    int: lambda a: str(a),
    float: lambda a: str(a),
    set: lambda a: ' '.join(a),
    str: lambda a: _html.escape(a)
}