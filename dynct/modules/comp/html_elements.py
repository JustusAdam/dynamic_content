"""
Framework for rendering HTML elements *incomplete*
"""

import html
import re
from dynct.errors import InvalidInputError

__author__ = 'justusadam'


class BaseElement:
    """
    Please note: '_customs' is not to be modified from outside the class, it is purely an easy way for subclasses to add
    custom properties without having to change the render function(s).
    Rule of thumb is that _customs should be used for any additional, visible properties mentioned in the constructor of
    your inheriting class, unless you require a more complex setter
    """

    def __init__(self, html_type, additionals:dict=None):
        self.html_type = html_type
        self.additionals = additionals
        self._customs = {}


    def render_additionals(self):
        if not self.additionals:
            return ''
        elif isinstance(self.additionals, str):
            return self.additionals
        else:
            return list(k + '="' + html.escape(v) + '"' for k, v in self.additionals.items())


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
        l = [self.html_type]
        if self._customs:
            l += self.render_customs()
        if self.additionals:
            l += self.render_additionals()
        return '<' + ' '.join(l) + '>'

    def __str__(self):
        return self.render()


class BaseClassIdElement(BaseElement):
    _classes = None

    def __init__(self, html_type, classes:set=None, element_id:str=None, additionals:dict=None):
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
    _list_replacement = None
    def __init__(self, *content, html_type='div', classes:set=None, element_id:str=None, additionals:dict=None):
        super().__init__(html_type, classes, element_id, additionals)
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
        return ''.join(list(str(a) for a in self._content))

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
    def __init__(self, href, *content, classes:set=None, element_id:str=None, additionals:dict=None):
        super().__init__(*content, html_type='a', classes=classes, element_id=element_id, additionals=additionals)
        self._customs['href'] = href


class HTMLPage(ContainerElement):
    _stylesheets = None
    _metatags = None
    _scripts = None

    def __init__(self, title, *content, classes:set=None, element_id:str=None, additionals:dict=None, metatags:set=None,
                 stylesheets:set=None, scripts:set=None):
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
    def __init__(self, href, rel, element_type:str=None, additionals:dict=None):
        super().__init__('link', additionals)
        self._customs['rel'] = rel
        self._customs['href'] = href
        self._customs['type'] = element_type


class Stylesheet(BaseElement):
    def __init__(self, href, media='all', typedec='text/css', rel='stylesheet', additionals:dict=None):
        super().__init__('link', additionals)
        self._customs['href'] = href
        self._customs['media'] = media
        self._customs['type'] = typedec
        self._customs['rel'] = rel


class Script(ContainerElement):
    def __init__(self, *content, src:str=None, prop_type='text/javascript', additionals:dict=None):
        super().__init__(*content, html_type='script', additionals=additionals)
        self._customs['type'] = prop_type
        self._customs['src'] = src


class List(AbstractList):
    def __init__(self, *content, list_type='ul', classes:set=None, element_id:str=None, additionals:dict=None,
                 item_classes:set=None, item_additional_properties:dict=None):
        self.item_classes = item_classes
        self.item_additionals = item_additional_properties
        super().__init__(*content, html_type=list_type, classes=classes, element_id=element_id, additionals=additionals)

    def ensure_subtype(self, value):
        if isinstance(value, BaseClassIdElement) and value.html_type in self._subtypes:
            value.classes |= self.item_classes
            value.additionals.update(self.item_additionals)
            return value
        else:
            return super().ensure_subtype(value)

    def subtype_wrapper(self, *args):
        return ContainerElement(*args, html_type=self._subtypes[0], classes=self.item_classes, additionals=self.item_additionals)


class Select(AbstractList):
    _subtypes = ['option']
    def __init__(self, *content, classes:set=None, element_id:str=None, additionals:dict=None, form:str=None, required:bool=False, disabled=False, name:str=None, selected:str=None):
        self.selected = selected
        super().__init__(*content, html_type='select', classes=classes, element_id=element_id, additionals=additionals)
        self._customs['form'] = form
        self._customs['name'] = name
        self.required = required
        self.disabled = disabled

    def subtype_wrapper(self, value, content):
        return Option(content, value=value, selected=self.selected == value)

    def render_head(self):
        head = [super().render_head()]
        if self.required:
            head.append('required')
        if self.disabled:
            head.append('disabled')
        return ' '.join(head)


class Option(ContainerElement):
    def __init__(self, *content, selected=False, value:str=None):
        super().__init__(*content, html_type='option')
        self._customs['value'] = value
        self.selected = selected

    def render_head(self):
        if self.selected:
            return super().render_head() + ' selected'
        else:
            return super().render_head()


class TableElement(ContainerElement):
    def __init__(self, *content, classes:set=None, element_id:str=None, additionals:dict=None, table_head=False):
        self.table_head = table_head
        super().__init__(*content, html_type='table', classes=classes, element_id=element_id, additionals=additionals)


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
    def __init__(self, *content, classes:set=None, element_id:str=None, additionals:dict=None):
        super().__init__(*content, html_type='tr', classes=classes, element_id=element_id, additionals=additionals)

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
    def __init__(self, *content, classes:set=None, element_id:str=None, additionals:dict=None):
        super().__init__(*content, classes=classes, element_id=element_id, additionals=additionals)
        self.html_type = 'th'


class TableData(ContainerElement):
    def __init__(self, *content, classes:set=None, element_id:str=None, additionals:dict=None):
        super().__init__(*content, html_type='td', classes=classes, element_id=element_id, additionals=additionals)


class Input(BaseClassIdElement):
    def __init__(self, classes:set=None, element_id:str=None, input_type='text', name:str=None, form:str=None,
                 value:str=None, required=False, additionals:dict=None):
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


class TextInput(Input):
    def __init__(self, classes:set=None, element_id:str=None, name:str=None, form:str=None,
                 value:str=None, size:int=60, required=False, additionals:dict=None):
        super().__init__(classes=classes, element_id=element_id, input_type='text', name=name, form=form,
                 value=value, required=required, additionals=additionals)
        self._customs['size'] = size


class Radio(Input):
    def __init__(self, classes:set=None, element_id:str=None, name:str=None, form:str=None, value:str=None,
                 required=False, checked=False, additionals:dict=None):
        super().__init__(classes=classes, element_id=element_id, input_type='radio', name=name, form=form,
                         value=value,
                         required=required, additionals=additionals)
        if checked:
            self._customs['checked'] = 'checked'


class Checkbox(Input):
    def __init__(self, classes:set=None, element_id:str=None, name:str=None, form:str=None, value:str=None,
                 required=False, checked=False, additionals:dict=None):
        super().__init__(classes=classes, element_id=element_id, input_type='checkbox', name=name, form=form,
                         value=value,
                         required=required, additionals=additionals)
        if checked:
            self._customs['checked'] = 'checked'


class Textarea(ContainerElement):
    def __init__(self, *content, classes:set=None, element_id:str=None, name:str=None, form:str=None, required=False,
                 rows=0, cols=0, additionals:dict=None):
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
    def __init__(self, *content, label_for:str=None, classes:set=None, element_id:str=None, additionals:dict=None):
        super().__init__(*content, html_type='label', classes=classes, element_id=element_id, additionals=additionals)
        self._customs['label'] = label_for


class SubmitButton(Input):
    def __init__(self, value='Submit', classes:set=None, element_id:str=None, name:str=None, form:str=None,
                 additionals:dict=None):
        super().__init__(value=value, classes=classes, element_id=element_id, name=name, input_type='submit', form=form,
                         additionals=additionals)


class FormElement(ContainerElement):
    def __init__(self, *content, action='{this}', classes:set=None, element_id:str=None, method='post', charset='UTF-8',
                 submit=SubmitButton(), target:str=None, additionals:dict=None):
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