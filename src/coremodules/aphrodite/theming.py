import re
from src.coremodules.dionysus.commons import get_common_elements


__author__ = 'justusadam'


def layout(blocks):
    result = get_db_connection().execute(query='SELECT region, block_name FROM blocks WHERE block_name IN (' +
                                    blocks.toString()[1:-1] +
                                    ') ORDERED BY region, weight')

    return {}


def get_current_theme():
    return 'default_theme'


def get_defined_fields(template, theme=get_current_theme()):
    """
    Acquire a full list of all variables occurring in the given template
    :return:
    """
    template_path = get_theme_path(theme=theme) + '/template/' + template + '.html'
    file = open(file=template_path, mode='r')
    return [x[1:-1] for x in re.findall(r'\{[_\w\s-]+\}', file.read())]


def fill_replacement_pattern(page_id, unique_page_type):

    pattern = \
        dict([(variable, '') for variable in
              get_defined_fields(template='page')])

    content_type_information = get_content_type_information(id=page_id, unique_page_type=unique_page_type)

    # obtain commons
    if content_type_information['blocks']:
        blocks = get_common_elements(page_id=page_id, unique_page_type=unique_page_type)

        pattern.update(layout(blocks=blocks))

    return pattern


def get_content_type_information(id, unique_page_type):
    if unique_page_type == 'setup':
        return {
            'blocks': False
        }
    return {
        'blocks': True
    }


def get_theme_path(theme):
    return 'themes/' + theme


def parse_template(pattern, template, theme=get_current_theme()):
    template_path = get_theme_path(theme=theme) + '/template/' + template + '.html'
    template = open(file=template_path, mode='r')
    template = template.read()
    return template.format(**pattern)
