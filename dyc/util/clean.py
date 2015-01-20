import itertools
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


def clean_text(text, forbidden_tags):
    for tag in forbidden_tags:
        regex2 = re.compile('<' + tag + '.*?>', flags=re.S)
        regex3 = re.compile('</' + tag + '.*?>', flags=re.S)
        text = re.sub(regex2, '', text)
        text = re.sub(regex3, '', text)
    return text
