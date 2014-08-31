__author__ = 'justusadam'


BASEDIR = 'localhost:8000'


def html_element(*contents, html_type='div', classes='', element_id='', additional_properties=''):
    frame = ['<' + html_type]
    if classes:
        if isinstance(classes, list) or isinstance(classes, tuple):
            classes = ' '.join(classes)
        frame += ['class="' + classes + '"']
    if element_id:
        frame += ['id="' + element_id + '"']
    if additional_properties:
        if isinstance(additional_properties, list) or isinstance(additional_properties, tuple):
            additional_properties = ' '.join(additional_properties)
        frame += [additional_properties]
    frame[-1] += '>'
    return ' '.join(frame) + ''.join(contents) + '</' + html_type + '>'


def closed_html_element(html_type='div', classes='', element_id='', additional_properties=''):
    frame = ['<' + html_type]
    if classes:
        if isinstance(classes, list) or isinstance(classes, tuple):
            classes = ' '.join(classes)
        frame += ['class="' + classes + '"']
    if element_id:
        frame += ['id="' + element_id + '"']
    if additional_properties:
        if isinstance(additional_properties, list) or isinstance(additional_properties, tuple):
            additional_properties = ' '.join(additional_properties)
        frame += [additional_properties]
    frame += ['/>']
    return ' '.join(frame)


def list_element(*contents, list_type='ul', classes='', element_id='', additional_properties='',
                 sublist_classes='', sublist_additional_properties=''):
    new_contents = [
        html_element(element, html_type='li', classes=sublist_classes,
                     additional_properties=sublist_additional_properties) for element in contents]
    return html_element(*new_contents, html_type=list_type, classes=classes, element_id=element_id,
                        additional_properties=additional_properties)


def table_element(*contents, classes='', element_id='', additional_properties=''):
    new_contents = [tr_element(*elements) for elements in contents]
    return html_element(*new_contents, html_type='table', classes=classes, element_id=element_id,
                        additional_properties=additional_properties)


def tr_element(*contents, classes='', element_id='', additional_properties=''):
    new_contents = [html_element(*element, html_type='td') for element in contents]
    return html_element(*new_contents, html_type='tr', classes=classes, element_id=element_id,
                        additional_properties=additional_properties)


def input_element(classes='', element_id='', input_type='text', name='', end_line=True, form='', additional_properties=''):
    input_properties = ['type="' + input_type + '"']
    if form:
        input_properties = ['form="' + form + '"'] + input_properties
    if name:
        input_properties = ['name="' + name + '"'] + input_properties
    if isinstance(additional_properties, str):
        additional_properties = [additional_properties]
    element = closed_html_element(html_type='input', classes=classes, element_id=element_id,
                                  additional_properties=input_properties + additional_properties)
    if end_line:
        element += '<br />'
    return element


def submit_input_element(value='Submit', classes='', element_id='', name='submit',
                         end_line=False, form='', additional_properties=''):
    submit_properties = ['value="' + value + '"']
    if isinstance(additional_properties, str):
        additional_properties = [additional_properties]
    return input_element(classes=classes, element_id=element_id, input_type='submit', name=name,
                         end_line=end_line, form=form, additional_properties=submit_properties + additional_properties)


def form_element(*contents, classes='', element_id='',
                 action='/', method='post', charset='UTF-8',
                 submit=submit_input_element(), target='_self', additional_properties=''):
    form_properties = ['action="' + action + '"',
                       'method="' + method + '"',
                       'target="' + target + '"',
                       'accept-charset="' + charset + '"']
    new_content = contents + (submit,)
    if isinstance(additional_properties, str):
        additional_properties = [additional_properties]
    return html_element(*new_content, html_type='form', classes=classes, element_id=element_id,
                        additional_properties=form_properties + additional_properties)


def stylesheet_link(link, html_type='text/css'):
    return '<link rel="stylesheet" href="' + link + '" type="' + html_type + '" />'


def test():
    print(html_element())
    print(html_element(html_element(), html_type='html', classes=['main', 'hellooo']))


if __name__ == '__main__':
    test()