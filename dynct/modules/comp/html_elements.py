"""
Framework for rendering HTML elements *incomplete*
"""

import html
import re

from dynct.util.html import to_html_head
from dynct.errors import InvalidInputError

__author__ = 'justusadam'


class BaseElement:
    """
    Please note: '_customs' is not to be modified from outside the class, it is purely an easy way for subclasses to add
    custom properties without having to change the render function(s).
    Rule of thumb is that _customs should be used for any additional, visible properties mentioned in the constructor of
    your inheriting class, unless you require a more complex setter and/or way of rendering.
    """

    def __init__(self, html_type, additional:dict=None):
        self.html_type = html_type
        if additional:
            self._value_params = dict(additional)
        else:
            self._value_params = {}
        self._params = set()

    def render_value_params(self):
        return [str(k) + '="' + html.escape(v) + '"' for k,v in self._value_params.items() if v]

    def __add__(self, other):
        return str(self) + str(other)

    def render_head(self):
        return to_html_head(self.html_type, self._value_params, self._params)

    def render(self):
        return '<' + self.render_head() + '>'

    def __str__(self):
        return self.render()


class BaseClassIdElement(BaseElement):
    def __init__(self, html_type, classes:set=None, element_id:str=None, additional:dict=None):
        super().__init__(html_type, additional)
        self._value_params['class'] = classes
        self._value_params['id'] = element_id

    @property
    def classes(self):
        return self._value_params['class']

    @classes.setter
    def classes(self, val):
        self._value_params['class'] = val

    @property
    def element_id(self):
        return self._value_params['id']

    @element_id.setter
    def element_id(self, val):
        self._value_params['id'] = val


class ContainerElement(BaseClassIdElement):
    _list_replacement = None
    def __init__(self, *content, html_type='div', classes:set=None, element_id:str=None, additional:dict=None):
        super().__init__(html_type, classes, element_id, additional)
        self.content = content

    @property
    def list_replacement(self):
        if self._list_replacement:
            return self._list_replacement
        else:
            return ContainerElement

    @property
    def content(self):
        return self._content

    @content.setter
    def content(self, value):
        if isinstance(value, str):
            self._content = [value]
        elif hasattr(value, '__iter__'):
            self._content = list(self.ensure_type(v) for v in value)
        else:
            self._content = value

    def ensure_type(self, value):
        if isinstance(value, (list, tuple)):
            return self.list_replacement(*value)
        else:
            return value

    def render_content(self):
        return ''.join(str(a) for a in self._content)

    def render(self):
        return '<' + self.render_head() + '>' + self.render_content() + '</' + self.html_type + '>'


class AbstractList(ContainerElement):
    _subtypes = ['li']
    _regex = re.compile('<(\w+)')

    def subtype_wrapper(self, *args, **kwargs):
        return ContainerElement(*args, html_type=self._subtypes[0], **kwargs)

    @property
    def content(self):
        return self._content

    @content.setter
    def content(self, val):
        self._content = list(self.ensure_subtype(v) for v in val)

    def ensure_subtype(self, value):
        if isinstance(value, str):
            m = self._regex.match(value)
            if m and m.group(1) in self._subtypes:
                return value
            else:
                return self.subtype_wrapper(value)
        elif isinstance(value, BaseElement) and value.html_type in self._subtypes:
            return value
        elif isinstance(value, (list, tuple)):
            return self.subtype_wrapper(*value)
        else:
            return self.subtype_wrapper(value)



class A(ContainerElement):
    def __init__(self, href, *content, classes:set=None, element_id:str=None, additional:dict=None):
        super().__init__(*content, html_type='a', classes=classes, element_id=element_id, additional=additional)
        self._value_params['href'] = href


class HTMLPage(ContainerElement):
    _stylesheets = None
    _metatags = None
    _scripts = None

    def __init__(self, title, *content, classes:set=None, element_id:str=None, additional:dict=None, metatags:set=None,
                 stylesheets:set=None, scripts:set=None):
        super().__init__(title, *content, html_type='html', classes=classes, element_id=element_id,
                         additional=additional)
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
    def __init__(self, href, rel, element_type:str=None, additional:dict=None):
        super().__init__('link', additional)
        self._value_params['rel'] = rel
        self._value_params['href'] = href
        self._value_params['type'] = element_type


class Stylesheet(BaseElement):
    def __init__(self, href, media='all', typedec='text/css', rel='stylesheet', additional:dict=None):
        super().__init__('link', additional)
        self._value_params['href'] = href
        self._value_params['media'] = media
        self._value_params['type'] = typedec
        self._value_params['rel'] = rel


class Script(ContainerElement):
    def __init__(self, *content, src:str=None, prop_type='text/javascript', additional:dict=None):
        super().__init__(*content, html_type='script', additional=additional)
        self._value_params['type'] = prop_type
        self._value_params['src'] = src


class List(AbstractList):
    def __init__(self, *content, list_type='ul', classes:set=None, element_id:str=None, additional:dict=None,
                 item_classes:set=None, item_additional_properties:dict=None):
        self.item_classes = item_classes
        self.item_additionals = item_additional_properties
        super().__init__(*content, html_type=list_type, classes=classes, element_id=element_id, additional=additional)

    def ensure_subtype(self, value):
        if isinstance(value, BaseClassIdElement) and value.html_type in self._subtypes:
            value.classes |= self.item_classes
            value._value_params.update(self.item_additionals)
            return value
        else:
            return super().ensure_subtype(value)

    def subtype_wrapper(self, *args):
        return ContainerElement(*args, html_type=self._subtypes[0], classes=self.item_classes, additional=self.item_additionals)


class Select(AbstractList):
    _subtypes = ['option']
    def __init__(self, *content, classes:set=None, element_id:str=None, additional:dict=None, form:str=None, required:bool=False, disabled=False, name:str=None, selected:str=None):
        self.selected = selected
        super().__init__(*content, html_type='select', classes=classes, element_id=element_id, additional=additional)
        self._value_params['form'] = form
        self._value_params['name'] = name
        if required:
            self._params.add('required')
        if disabled:
            self._params.add('disabled')

    def subtype_wrapper(self, value, content):
        return Option(content, value=value, selected=self.selected == value)


class Option(ContainerElement):
    def __init__(self, *content, selected=False, value:str=None):
        super().__init__(*content, html_type='option')
        self._value_params['value'] = value
        self.selected = selected

    def render_head(self):
        if self.selected:
            return super().render_head() + ' selected'
        else:
            return super().render_head()


class TableElement(ContainerElement):
    def __init__(self, *content, classes:set=None, element_id:str=None, additional:dict=None, table_head=False):
        self.table_head = table_head
        super().__init__(*content, html_type='table', classes=classes, element_id=element_id, additional=additional)

    @property
    def content(self):
        return self._content

    @content.setter
    def content(self, value):
        if isinstance(value, str):
            self._content = value
        elif self.table_head:
            self._content = [self.ensure_th(value[0])] + [self.ensure_tr(row) for row in value[1:]]
        else:
            self._content = [self.ensure_tr(row) for row in value]

    @staticmethod
    def ensure_tr(row):
        if isinstance(row, ContainerElement) and row.html_type == 'tr':
            return row
        elif isinstance(row, (list, tuple)):
            return TableRow(*row)
        return TableRow(row)

    @staticmethod
    def ensure_th(row):
        if isinstance(row, ContainerElement) and row.html_type == 'th':
            return str(row)
        elif isinstance(row, (list, tuple)):
            return str(TableHead(*row))
        return str(TableHead(row))


class TableRow(ContainerElement):
    def __init__(self, *content, classes:set=None, element_id:str=None, additional:dict=None):
        super().__init__(*content, html_type='tr', classes=classes, element_id=element_id, additional=additional)

    @property
    def content(self):
        return self._content

    @content.setter
    def content(self, value):
        if isinstance(value, str):
            self._content = value
        else:
            self._content = [self.ensure_td(row) for row in value]

    @staticmethod
    def ensure_td(row):
        if isinstance(row, ContainerElement) and row.html_type == 'td':
            return row
        elif isinstance(row, (list, tuple)):
            return TableData(*row)
        else:
            return TableData(row)


class TableHead(TableRow):
    def __init__(self, *content, classes:set=None, element_id:str=None, additional:dict=None):
        super().__init__(*content, classes=classes, element_id=element_id, additional=additional)
        self.html_type = 'th'


class TableData(ContainerElement):
    def __init__(self, *content, classes:set=None, element_id:str=None, additional:dict=None):
        super().__init__(*content, html_type='td', classes=classes, element_id=element_id, additional=additional)


class Input(BaseClassIdElement):
    def __init__(self, classes:set=None, element_id:str=None, input_type='text', name:str=None, form:str=None,
                 value:str=None, required=False, additional:dict=None):
        super().__init__('input', classes=classes, element_id=element_id, additional=additional)
        self._value_params['name'] = name
        self._value_params['type'] = input_type
        self._value_params['form'] = form
        self._value_params['value'] = value
        if required:
            self._params.add('required')

    def render(self):
        return '<' + self.render_head() + ' />'


class TextInput(Input):
    def __init__(self, classes:set=None, element_id:str=None, name:str=None, form:str=None,
                 value:str=None, size:int=60, required=False, additional:dict=None):
        super().__init__(classes=classes, element_id=element_id, input_type='text', name=name, form=form,
                 value=value, required=required, additional=additional)
        self._value_params['size'] = size


class Radio(Input):
    def __init__(self, classes:set=None, element_id:str=None, name:str=None, form:str=None, value:str=None,
                 required=False, checked=False, additional:dict=None):
        super().__init__(classes=classes, element_id=element_id, input_type='radio', name=name, form=form,
                         value=value,
                         required=required, additional=additional)
        if checked:
            self._value_params['checked'] = 'checked'


class Checkbox(Input):
    def __init__(self, classes:set=None, element_id:str=None, name:str=None, form:str=None, value:str=None,
                 required=False, checked=False, additional:dict=None):
        super().__init__(classes=classes, element_id=element_id, input_type='checkbox', name=name, form=form,
                         value=value,
                         required=required, additional=additional)
        if checked:
            self._value_params['checked'] = 'checked'


class Textarea(ContainerElement):
    def __init__(self, *content, classes:set=None, element_id:str=None, name:str=None, form:str=None, required=False,
                 rows=0, cols=0, additional:dict=None):
        super().__init__(*content, html_type='textarea', classes=classes, element_id=element_id,
                         additional=additional)
        self._value_params['name'] = name
        self._value_params['form'] = form
        self._value_params['rows'] = rows
        self._value_params['cols'] = cols
        if required:
            self._params.add('required')


class Label(ContainerElement):
    def __init__(self, *content, label_for:str=None, classes:set=None, element_id:str=None, additional:dict=None):
        super().__init__(*content, html_type='label', classes=classes, element_id=element_id, additional=additional)
        self._value_params['label'] = label_for


class SubmitButton(Input):
    def __init__(self, value='Submit', classes:set=None, element_id:str=None, name:str=None, form:str=None,
                 additional:dict=None):
        super().__init__(value=value, classes=classes, element_id=element_id, name=name, input_type='submit', form=form,
                         additional=additional)


class FormElement(ContainerElement):
    def __init__(self, *content, action='{this}', classes:set=None, element_id:str=None, method='post', charset='UTF-8',
                 submit=SubmitButton(), target:str=None, additional:dict=None):
        super().__init__(*content, html_type='form', classes=classes, element_id=element_id, additional=additional)
        self._value_params['method'] = method
        self._value_params['charset'] = charset
        self._value_params['target'] = target
        self._value_params['action'] = action
        self.submit = submit

    def render_content(self):
        return super().render_content() + str(self.submit)


# this recurses?
def container_wrapper(used_class, **kwargs):
    def wrapped(*args):
        return used_class(*args, **kwargs)

    return wrapped