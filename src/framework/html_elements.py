"""
Framework for rendering HTML elements *incomplete*
"""

__author__ = 'justusadam'


class ClassContainer:
    def __init__(self, *classes):
        self._classes = []
        for value in classes:
            if isinstance(value, str):
                self._classes += [value]
            if isinstance(value, list):
                self._classes += value
            if isinstance(value, tuple):
                self._classes += list(value)

    @property
    def classes(self):
        return self._classes

    @classes.setter
    def classes(self, value):
        if isinstance(value, str):
            self._classes = [value]
        if isinstance(value, list):
            self._classes = value
        if isinstance(value, tuple):
            self._classes = list(value)

    def __add__(self, other):
        if isinstance(other, str):
            self._classes += [other]
        if isinstance(other, list):
            self._classes += other
        if isinstance(other, tuple):
            self._classes += list(other)
        if isinstance(other, ClassContainer):
            self._classes += other.classes
        return self

    def __bool__(self):
        return bool(self._classes)

    def __len__(self):
        return len(self._classes)

    def __str__(self):
        return ' '.join(self._classes)

    def __getitem__(self, item):
        return self._classes[item]


class BaseElement:

    def __init__(self, html_type, additionals={}):
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
            return list(k + '="' + v + '"' for k, v in self.additionals.items())
        else:
            return self._additionals

    def render_customs(self):
        if isinstance(self._customs, dict):
            acc = []
            for k, v in self._customs.items():
                if v:
                    acc += [k + '="' + str(v) + '"']
            return acc

    def __add__(self, other):
        return str(self) + str(other)

    def __str__(self):
        return '<' + ' '.join([self.html_type] + self.render_customs() + self.render_additionals()) + '>'


class BaseClassIdElement(BaseElement):
    """
    Please note: '_customs' is not to be modified from outside the class, it is purely an easy way for subclasses to add
    custom properties without having to change the render function(s).
    """

    def __init__(self, html_type, classes=[], element_id='', additionals={}):
        super().__init__(html_type, additionals)
        self._classes = ClassContainer(classes)
        self.element_id = element_id

    @property
    def classes(self):
        return self._classes.classes

    @classes.setter
    def classes(self, value):
        self._classes.classes = [value]


    def render_head(self):
        frame = [self.html_type]
        if self.classes:
            frame += ['class="' + str(self._classes) + '"']
        if self.element_id:
            frame += ['id="' + self.element_id + '"']
        if self.additionals:
            frame += self.render_additionals()
        if self._customs:
            frame += self.render_customs()
        return ' '.join(frame)

    def __str__(self):
        return '<' + self.render_head() + '>'


class ContainerElement(BaseClassIdElement):

    def __init__(self, *contents, html_type='div', classes=[], element_id='', additionals={}):
        super().__init__(html_type, classes, element_id, additionals)
        self._content = contents

    @property
    def contents(self):
        return self._content

    @contents.setter
    def contents(self, value):
        if isinstance(value, str):
            self._content = [value]
        else:
            self._content = value

    def render_content(self):
        return ''.join(list(str(a) for a in self._content))

    def __str__(self):
        return '<' + self.render_head() + '>' + self.render_content() + '</' + self.html_type + '>'


class LinkElement(BaseElement):
    def __init__(self, href, rel, additionals={}):
        super().__init__('link', additionals)
        self._customs['rel'] = rel
        self._customs['href'] = href


class Stylesheet(BaseElement):

    def __init__(self, href, media='all', typedec='text/css', rel='stylesheet', additionals={}):
        super().__init__('link', additionals)
        self.href = href
        self.media = media
        self.typedec = typedec
        self.rel = rel

    def __str__(self):
        elements = [
            self.html_type,
            'rel="' + self.rel + '"',
            'type="' + self.typedec + '"',
            'media="' + self.media + '"',
            'href="' + self.href + '"'
        ]
        return '<' + ' '.join(elements + self.render_additionals() + self.render_customs()) + '>'


class Script(BaseElement):
    def __init__(self, src, prop_type='text/javascript', additionals=[]):
        super().__init__('script', additionals)
        self._customs['type'] = prop_type
        self._customs['src'] = src


class List(ContainerElement):

    def __init__(self, *contents, list_type='ul', classes=[], element_id='', additionals={}, item_classes=[],
                 item_additional_properties={}):
        super().__init__(*contents, html_type=list_type, classes=classes, element_id=element_id, additionals=additionals)
        self.item_classes = item_classes
        self.item_additionals = item_additional_properties

    def render_list_element(self, element):
        if isinstance(element, ContainerElement):
            if element.html_type == 'li':
                return str(element)
        else:
            return str(ContainerElement(element, html_type='li', classes=self.item_classes,
                                        additionals=self.item_additionals))

    def render_content(self):
        return ''.join(tuple(self.render_list_element(element) for element in self.contents))


class TableElement(ContainerElement):
    def __init__(self, *contents, classes=[], element_id='', additionals={}):
        super().__init__(*contents, html_type='table', classes=classes, element_id=element_id, additionals=additionals)

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
        return ''.join(tuple(self.render_table_row(element) for element in self.contents))


class Input(BaseClassIdElement):

    def __init__(self, classes=[], element_id='', input_type='text', name='', form='', value='', required=False, additionals={}):
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

    def __str__(self):
        return '<' + self.render_head() + ' />'


class Textarea(ContainerElement):
    def __init__(self, *contents, classes=[], element_id='', name='', form='', required=False, rows=0, cols=0, additionals={}):
        super().__init__(*contents, html_type='textarea', classes=classes, element_id=element_id, additionals=additionals)
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
    def __init__(self, *contents, label_for='', classes=[], element_id='', additionals={}):
        super().__init__(*contents, html_type='label', classes=classes, element_id=element_id, additionals=additionals)
        self._customs['label'] = label_for


class SubmitButton(Input):

    def __init__(self, value='Submit', classes=[], element_id='', name='submit', end_line=False, form='',
                 additionals={}):
        super().__init__(value=value, classes=classes, element_id=element_id, name=name, input_type='submit', form=form,
                         additionals=additionals)


class FormElement(ContainerElement):

    def __init__(self, *contents, action='{this}',classes=[], element_id='', method='post', charset='UTF-8',
                 submit=SubmitButton(), target='', additionals={}):
        super().__init__(*contents, html_type='form', classes=classes, element_id=element_id, additionals=additionals)
        self._customs['method'] = method
        self._customs['charset'] = charset
        self._customs['target'] = target
        self._customs['action'] = action
        self.submit = submit

    def render_content(self):
        return super().render_content() + str(self.submit)