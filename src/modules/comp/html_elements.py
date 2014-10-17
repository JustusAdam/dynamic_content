"""
Framework for rendering HTML elements *incomplete*
"""

import html

__author__ = 'justusadam'


class BaseElement:
    """
    Please note: '_customs' is not to be modified from outside the class, it is purely an easy way for subclasses to add
    custom properties without having to change the render function(s).
    Rule of thumb is that _customs should be used for any additional, visible properties mentioned in the constructor of
    your inheriting class, unless you require a more complex setter
    """

    def __init__(self, html_type, additionals=dict()):
        self.html_type = html_type
        if isinstance(additionals, str):
            additionals = [additionals]
        self._additionals = additionals
        self._customs = {}

    @property
    def additionals(self):
        return self._additionals

    @additionals.setter
    def additionals(self, value):
        if isinstance(value, str):
            self._additionals = [value]
        else:
            self._additionals = value

    def render_additionals(self):
        if isinstance(self.additionals, dict):
            return list(k + '="' + html.escape(v) + '"' for k, v in self.additionals.items())
        else:
            return self._additionals

    def render_customs(self):
        def render(item):
            if isinstance(item, str):
                return html.escape(item)
            elif isinstance(item, (list, tuple, set)):
                return ' '.join(list(html.escape(str(a)) for a in item))
            else:
                return html.escape(str(item))

        acc = []
        for k, v in self._customs.items():
            if v:
                acc += [k + '="' + render(v) + '"']
        return acc

    def __add__(self, other):
        return str(self) + str(other)

    def render(self):
        return '<' + ' '.join([self.html_type] + self.render_customs() + self.render_additionals()) + '>'

    def __str__(self):
        return self.render()


class BaseClassIdElement(BaseElement):
    _classes = None

    def __init__(self, html_type, classes=set(), element_id='', additionals={}):
        super().__init__(html_type, additionals)
        self.classes = classes
        self.element_id = element_id

    @property
    def classes(self):
        return self._classes

    @classes.setter
    def classes(self, value):
        if isinstance(value, set):
            self._classes = value
        elif isinstance(value, (list, tuple)):
            self._classes = set(value)
        elif isinstance(value, str):
            self._classes = {value}


    def render_head(self):
        frame = [self.html_type]
        if self.classes:
            frame += ['class="' + ' '.join(self._classes) + '"']
        if self.element_id:
            frame += ['id="' + self.element_id + '"']
        if self.additionals:
            frame += self.render_additionals()
        if self._customs:
            frame += self.render_customs()
        return ' '.join(frame)

    def render(self):
        return '<' + self.render_head() + '>'


class ContainerElement(BaseClassIdElement):
    def __init__(self, *content, html_type='div', classes=set(), element_id='', additionals={}):
        super().__init__(html_type, classes, element_id, additionals)
        self._content = list(content)

    @property
    def content(self):
        return self._content

    @content.setter
    def content(self, value):
        if isinstance(value, str):
            self._content = [value]
        elif hasattr(value, '__iter__'):
            self._content = list(value)
        else:
            self._content = value

    def render_content(self):
        return ''.join(list(str(a) for a in self._content))

    def render(self):
        return '<' + self.render_head() + '>' + self.render_content() + '</' + self.html_type + '>'


class HTMLPage(ContainerElement):
    _stylesheets = None
    _metatags = None
    _scripts = None

    def __init__(self, title, *content, classes=set(), element_id='', additionals={}, metatags=set(), stylesheets=set(),
                 scripts=set()):
        super().__init__(title, *content, html_type='html', classes=classes, element_id=element_id,
                         additionals=additionals)
        self.stylesheets = stylesheets
        self.metatags = metatags
        self.scripts = scripts

    @property
    def stylesheets(self):
        return self._stylesheets

    @stylesheets.setter
    def stylesheets(self, val):
        if isinstance(val, set):
            self._stylesheets = val
        elif isinstance(val, (list, tuple)):
            self._stylesheets = set(val)
        elif isinstance(val, str):
            self._stylesheets = {val}

    @property
    def metatags(self):
        return self._metatags

    @metatags.setter
    def metatags(self, val):
        if isinstance(val, set):
            self._metatags = val
        elif isinstance(val, (list, tuple)):
            self._metatags = set(val)
        elif isinstance(val, str):
            self._metatags = {val}

    @property
    def scripts(self):
        return self._scripts

    @scripts.setter
    def scripts(self, val):
        if isinstance(val, set):
            self._scripts = val
        elif isinstance(val, (list, tuple)):
            self._scripts = set(val)
        elif isinstance(val, str):
            self._scripts = {val}

    def add(self, other):
        self._stylesheets |= other.stylesheets
        self._metatags |= other.metatags
        self._scripts |= other.scripts
        self.content += other.content


class LinkElement(BaseElement):
    def __init__(self, href, rel, element_type='', additionals={}):
        super().__init__('link', additionals)
        self._customs['rel'] = rel
        self._customs['href'] = href
        self._customs['type'] = element_type


class Stylesheet(BaseElement):
    def __init__(self, href, media='all', typedec='text/css', rel='stylesheet', additionals={}):
        super().__init__('link', additionals)
        self.href = href
        self.media = media
        self.typedec = typedec
        self.rel = rel

    def render(self):
        elements = [
            self.html_type,
            'rel="' + self.rel + '"',
            'type="' + self.typedec + '"',
            'media="' + self.media + '"',
            'href="' + self.href + '"'
        ]
        return '<' + ' '.join(elements + self.render_additionals() + self.render_customs()) + '>'


class Script(BaseElement):
    def __init__(self, src, prop_type='text/javascript', additionals={}):
        super().__init__('script', additionals)
        self._customs['type'] = prop_type
        self._customs['src'] = src


class List(ContainerElement):
    def __init__(self, *content, list_type='ul', classes=set(), element_id='', additionals={}, item_classes=set(),
                 item_additional_properties={}):
        super().__init__(*content, html_type=list_type, classes=classes, element_id=element_id, additionals=additionals)
        self.item_classes = item_classes
        self.item_additionals = item_additional_properties

    def render_list_element(self, element):
        if isinstance(element, ContainerElement):
            if element.html_type == 'li':
                return str(element)
        elif isinstance(element, str):
            return str(ContainerElement(element, html_type='li', classes=self.item_classes,
                                        additionals=self.item_additionals))
        elif hasattr(element, '__iter__'):
            return str(ContainerElement(*element, html_type='li', classes=self.item_classes,
                                        additionals=self.item_additionals))
        return str(ContainerElement(element, html_type='li', classes=self.item_classes,
                                    additionals=self.item_additionals))

    def render_content(self):
        return ''.join(tuple(self.render_list_element(element) for element in self.content))


class TableElement(ContainerElement):
    def __init__(self, *content, classes=set(), element_id='', additionals={}):
        super().__init__(*content, html_type='table', classes=classes, element_id=element_id, additionals=additionals)

    def render_table_row(self, row):
        if isinstance(row, ContainerElement):
            if row.html_type == 'tr':
                return str(row)
        elif isinstance(row, (list, tuple)):
            return '<tr>' + ''.join(tuple(self.render_table_data(data) for data in row)) + '</tr>'
        return '<tr>' + self.render_table_data(row) + '</tr>'

    def render_table_data(self, data):
        if isinstance(data, ContainerElement):
            if data.html_type == 'td':
                return str(data)
        return '<td>' + str(data) + '</td>'

    def render_content(self):
        return ''.join(tuple(self.render_table_row(element) for element in self.content))


class Input(BaseClassIdElement):
    def __init__(self, classes=set(), element_id='', input_type='text', name='', form='', value='', required=False,
                 additionals={}):
        super().__init__('input', classes=classes, element_id=element_id, additionals=additionals)
        self._customs['name'] = name
        self._customs['type'] = input_type
        self._customs['form'] = form
        self._customs['value'] = value
        self.required = required

    def render_head(self):
        head = super().render_head()
        if self.required:
            return head + ' required'
        else:
            return head

    def render(self):
        return '<' + self.render_head() + ' />'


class Radio(Input):
    def __init__(self, classes=set(), element_id='', name='', form='', value='', required=False,
                 checked=False, additionals={}):
        super().__init__(classes=classes, element_id=element_id, input_type='radio', name=name, form=form,
                         value=value,
                         required=required, additionals=additionals)
        self.checked = checked

    def render_head(self):
        if self.checked:
            return super().render_head() + ' checked'
        else:
            return super().render_head()


class Textarea(ContainerElement):
    def __init__(self, *content, classes=set(), element_id='', name='', form='', required=False, rows=0, cols=0,
                 additionals={}):
        super().__init__(*content, html_type='textarea', classes=classes, element_id=element_id,
                         additionals=additionals)
        self._customs['name'] = name
        self._customs['form'] = form
        self._customs['rows'] = rows
        self._customs['cols'] = cols
        self.required = required

    def render_head(self):
        head = super().render_head()
        if self.required:
            return head + ' required'
        else:
            return head


class Label(ContainerElement):
    def __init__(self, *content, label_for='', classes=set(), element_id='', additionals={}):
        super().__init__(*content, html_type='label', classes=classes, element_id=element_id, additionals=additionals)
        self._customs['label'] = label_for


class SubmitButton(Input):
    def __init__(self, value='Submit', classes=set(), element_id='', name='', form='',
                 additionals={}):
        super().__init__(value=value, classes=classes, element_id=element_id, name=name, input_type='submit', form=form,
                         additionals=additionals)


class FormElement(ContainerElement):
    def __init__(self, *content, action='{this}', classes=set(), element_id='', method='post', charset='UTF-8',
                 submit=SubmitButton(), target='', additionals={}):
        super().__init__(*content, html_type='form', classes=classes, element_id=element_id, additionals=additionals)
        self._customs['method'] = method
        self._customs['charset'] = charset
        self._customs['target'] = target
        self._customs['action'] = action
        self.submit = submit

    def render_content(self):
        return super().render_content() + str(self.submit)


# this recurses?
def container_wrapper(used_class, **kwargs):
    def wrapped(*args):
        return used_class(*args, **kwargs)

    return wrapped