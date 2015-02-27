"""Cleaning tools to remove dangeros html tags"""

import itertools
import functools
import re

__author__ = 'Justus Adam'
__version__ = '0.1'


severities = {
    0: ('iframe', 'script', 'link'),
    1: ('h1', 'h2', 'html', 'body', 'head'),
    2: ('div', '?dchp')
}

escapers = {'code', 'pre'}


def remove_dangerous_tags(text, severity_level=1):
    forbidden = tuple(itertools.chain(*tuple(severities[a] for a in range(severity_level + 1))))
    return clean_text(text, forbidden)


_cached_regex_provider = functools.lru_cache()(
    functools.partial(re.compile, pattern, flags=re.S)
)


def clean_text(text, forbidden_tags):
    """
    Remove all tags in forbidden_tags from input text

    :param forbidden_tags: tags to remove
    :return: cleaned text
    """
    for tag in forbidden_tags:
        regex2 = _cached_regex_provider('<' + tag + '.*?>')
        regex3 = _cached_regex_provider('</' + tag + '.*?>')
        text = re.sub(regex2, '', text)
        text = re.sub(regex3, '', text)
    return text
