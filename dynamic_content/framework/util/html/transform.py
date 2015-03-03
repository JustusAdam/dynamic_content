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

    # we need these two stacked generators because
    # calling _to_html_head with a non-empty dict
    # where all values are bool(value)==False
    # returns an '' which will result in it getting
    # joined and producing a rogue ' '
    # so we need to filter for empty strings AFTER
    # running _to_html_head
    return ' '.join(b for b in (_to_html_head(a) for a in items) if b != '')


def _to_html_head(item):
    if item is None:
        return None
    if isinstance(item, str):
        # have to test for str first because we
        # handle arbitrary iterable types later
        # and str implements the __iter__ method
        # used to identify iterable types
        return _html.escape(item)
    elif isinstance(item, dict):
        # we handle dict next because it too implements
        # the __iter__ method but only iterates keys
        # and we want keys + values
        return ' '.join(
            '{}="{}"'.format(
                _to_html_head(k), _to_html_head(v))
            for k, v in item.items() if v
        )
    elif hasattr(item, '__iter__'):
        # handling arbitrary iterable types
        # this should include generators
        return ' '.join(_to_html_head(a) for a in item if a)
    else:
        return _html.escape(str(item))