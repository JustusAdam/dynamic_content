"""Transform stuff to things related to html"""
import html as _html


__author__ = 'Justus Adam'
__version__ = '0.1.2'


def to_html_head(*items):
    """
    Layout *items in a manner that resembles the inside of an opening html tag

    :param items: items to transform
    :return: str
    """
    return ' '.join(_to_html_head(a) for a in items if a)


def _to_html_head(item):
    if isinstance(item, str):
        return _html.escape(item)
    elif isinstance(item, dict):
        return ' '.join(
            '{}="{}"'.format(
                _to_html_head(k), _to_html_head(v))
            for k, v in item.items() if v
        )
    elif hasattr(item, '__iter__'):
        return ' '.join(_to_html_head(a) for a in item if a)
    else:
        return _html.escape(str(item))