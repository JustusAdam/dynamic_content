"""
Framework for rendering HTML elements *incomplete*
"""

import re
import functools

from . import transform


__author__ = 'Justus Adam'
__version__ = '0.2'


class BaseElement:
    """
    Base element for html abstracting elements that can be rendered to string
    """
    # I tried to make the memory fingerprint smaller with this
    # however this does not work with multiple inheritance
    # __slots__ = ('_value_params', '_params', 'html_type')

    def __init__(self, html_type, additional:dict=None):
        self.html_type = html_type
        if additional:
            self._value_params = dict(additional)
        else:
            self._value_params = {}
        self._params = set()

    @property
    def params(self):
        return self._params

    @property
    def value_params(self):
        return self._value_params

    def __add__(self, other):
        return str(self) + str(other)

    def render_head(self):
        return transform.to_html_head(
            self.html_type,
            self._value_params,
            self._params
        )

    def render(self):
        return '<{}>'.format(self.render_head())

    def __str__(self):
        return self.render()

    def to_iter(self):
        return self.render()


class BaseClassIdElement(BaseElement):
    # I tried to make the memory fingerprint smaller with this
    # however this does not work with multiple inheritance
    # __slots__ = ()

    def __init__(
        self,
        html_type,
        classes:set=None,
        element_id:str=None,
        additional:dict=None
    ):
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


class ContainerElement(list, BaseClassIdElement):
    # I tried to make the memory fingerprint smaller with this
    # however this does not work with multiple inheritance
    # __slots__ = ()

    _list_replacement = None

    def __init__(
        self,
        *content,
        html_type='div',
        classes:set=None,
        element_id:str=None,
        additional:dict=None
    ):
        super().__init__(content)
        BaseClassIdElement.__init__(
            self,
            html_type,
            classes,
            element_id,
            additional
        )

    @property
    def content(self):
        return self

    @property
    def list_replacement(self):
        return (self._list_replacement
            if self._list_replacement is not None
            else ContainerElement)

    def ensure_type(self, value):
        if isinstance(value, (list, tuple)):
            return self.list_replacement(*value)
        else:
            return value

    def render_content(self):
        return ''.join(str(a) for a in self)

    def render(self):
        return '<{}>{}</{}>'.format(self.render_head(), self.render_content(), self.html_type)

    def iter_content(self):
        for a in self.content:
            if hasattr(a, 'to_iter'):
                for b in a.to_iter():
                    yield b
            else:
                yield a

    def to_iter(self):
        yield '<{}>'.format(self.render_head())
        for a in self.iter_content():
            yield a
        yield '</{}>'.format(self.html_type)


Div = functools.partial(ContainerElement, html_type='div')

Span = functools.partial(ContainerElement, html_type='span')


class AbstractList(ContainerElement):
    # I tried to make the memory fingerprint smaller with this
    # however this does not work with multiple inheritance
    # __slots__ = ()

    _subtypes = 'li',
    _regex = re.compile('<(\w+)')

    def subtype_wrapper(self, *args, **kwargs):
        return ContainerElement(*args, html_type=self._subtypes[0], **kwargs)

    def render_content(self):
        return ''.join(str(self.ensure_subtype(a)) for a in self)

    def ensure_subtype(self, value):
        if isinstance(value, str):
            m = self._regex.match(value)
            if m and m.group(1) in self._subtypes:
                return value
            else:
                return self.subtype_wrapper(value)
        elif (isinstance(value, BaseElement)
              and value.html_type in self._subtypes):
            return value
        elif hasattr(value, '__iter__'):
            return self.subtype_wrapper(*value)
        else:
            return self.subtype_wrapper(value)


class A(ContainerElement):
    # I tried to make the memory fingerprint smaller with this
    # however this does not work with multiple inheritance
    # __slots__ = ()

    def __init__(
        self,
        *content,
        href='',
        classes:set=None,
        element_id:str=None,
        additional:dict=None
    ):
        super().__init__(
            *content,
            html_type='a',
            classes=classes,
            element_id=element_id,
            additional=additional
        )
        self._value_params['href'] = href


class HTMLPage(ContainerElement):
    # I tried to make the memory fingerprint smaller with this
    # however this does not work with multiple inheritance
    # __slots__ = '_stylesheets', '_metatags', '_scripts'

    _stylesheets = None
    _metatags = None
    _scripts = None

    def __init__(
        self,
        title,
        *content,
        classes:set=None,
        element_id:str=None,
        additional:dict=None,
        metatags:set=None,
        stylesheets:set=None,
        scripts:set=None
    ):
        super().__init__(
            title,
            *content,
            html_type='html',
            classes=classes,
            element_id=element_id,
            additional=additional
        )
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
        self.extend(other)


class LinkElement(BaseElement):
    # I tried to make the memory fingerprint smaller with this
    # however this does not work with multiple inheritance
    # __slots__ = ()

    def __init__(
        self,
        href,
        rel,
        element_type:str=None,
        additional:dict=None
    ):
        super().__init__('link', additional)
        self._value_params['rel'] = rel
        self._value_params['href'] = href
        self._value_params['type'] = element_type


class Stylesheet(BaseElement):
    # I tried to make the memory fingerprint smaller with this
    # however this does not work with multiple inheritance
    # __slots__ = ()

    def __init__(
        self,
        href,
        media='all',
        typedec='text/css',
        rel='stylesheet',
        additional:dict=None
    ):
        super().__init__('link', additional)
        self._value_params['href'] = href
        self._value_params['media'] = media
        self._value_params['type'] = typedec
        self._value_params['rel'] = rel


class Script(ContainerElement):
    # I tried to make the memory fingerprint smaller with this
    # however this does not work with multiple inheritance
    # __slots__ = ()

    def __init__(
        self,
        *content,
        src: str=None,
        prop_type='text/javascript',
        additional: dict=None
    ):
        super().__init__(
            *content,
            html_type='script',
            additional=additional
        )
        self._value_params['type'] = prop_type
        self._value_params['src'] = src


class List(AbstractList):
    # I tried to make the memory fingerprint smaller with this
    # however this does not work with multiple inheritance
    # __slots__ = 'item_classes', 'item_additionals'

    def __init__(
        self,
        *content,
        list_type='ul',
        classes:set=None,
        element_id:str=None,
        additional:dict=None,
        item_classes:set=None,
        item_additional_properties:dict=None
    ):
        self.item_classes = item_classes
        self.item_additionals = item_additional_properties
        super().__init__(
            *content,
            html_type=list_type,
            classes=classes,
            element_id=element_id,
            additional=additional
        )

    def ensure_subtype(self, value):
        value = super().ensure_subtype(value)

        if self.item_classes is not None:
            value.classes = (
                self.item_classes
                if value.classes is None
                else set(value.classes) | self.item_classes
                )
        if self.item_additionals is not None:
            value._value_params.update(self.item_additionals)
        return value

    def subtype_wrapper(self, *args):
        return ContainerElement(*args, html_type=self._subtypes[0], classes=self.item_classes,
                                additional=self.item_additionals)

Li = List


class Select(AbstractList):
    # I tried to make the memory fingerprint smaller with this
    # however this does not work with multiple inheritance
    # __slots__ = 'selected',

    _subtypes = ['option']

    def __init__(
        self,
        *content,
        classes:set=None,
        element_id:str=None,
        additional:dict=None,
        form:str=None,
        required:bool=False,
        disabled=False,
        name:str=None,
        selected:str=None
    ):
        self.selected = selected
        super().__init__(
            *content,
            html_type='select',
            classes=classes,
            element_id=element_id,
            additional=additional
        )
        self._value_params['form'] = form
        self._value_params['name'] = name
        if required:
            self._params.add('required')
        if disabled:
            self._params.add('disabled')

    def subtype_wrapper(self, value, content):
        return Option(content, value=value, selected=self.selected == value)


class Option(ContainerElement):
    # I tried to make the memory fingerprint smaller with this
    # however this does not work with multiple inheritance
    # __slots__ = 'selected',

    def __init__(
        self,
        *content,
        selected=False,
        value:str=None
    ):
        super().__init__(*content, html_type='option')
        self._value_params['value'] = value
        self.selected = selected

    def render_head(self):
        if self.selected:
            return super().render_head() + ' selected'
        else:
            return super().render_head()


class TableElement(ContainerElement):
    # I tried to make the memory fingerprint smaller with this
    # however this does not work with multiple inheritance
    # __slots__ = 'table_head',

    def __init__(
        self,
        *content,
        classes:set=None,
        element_id:str=None,
        additional:dict=None,
        table_head=False
    ):
        self.table_head = table_head
        super().__init__(
            *content,
            html_type='table',
            classes=classes,
            element_id=element_id,
            additional=additional
        )

    def render_content(self):
        def compile_c():
            if self.table_head:
                yield self.ensure_th(self[0])
                iterable = self[1:]
            else:
                iterable = self
            for row in iterable:
                yield self.ensure_tr(row)

        return ''.join(str(a) for a in compile_c())

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


class AbstractTableRow(ContainerElement):
    # I tried to make the memory fingerprint smaller with this
    # however this does not work with multiple inheritance
    # __slots__ = ()

    def __init__(
        self,
        *content,
        html_type: str=None,
        classes: set=None,
        element_id: str=None,
        additional: dict=None
    ):
        super().__init__(
            *content,
            html_type=html_type,
            classes=classes,
            element_id=element_id,
            additional=additional
        )

    def render_content(self):
        return ''.join(str(self.ensure_td(row)) for row in self)

    @staticmethod
    def ensure_td(row):
        if isinstance(row, ContainerElement) and row.html_type == 'td':
            return row
        elif isinstance(row, (list, tuple)):
            return TableData(*row)
        else:
            return TableData(row)


TableHead = functools.partial(AbstractTableRow, html_type='th')

TableRow = functools.partial(AbstractTableRow, html_type='tr')

TableData = functools.partial(ContainerElement, html_type='td')


class Input(BaseClassIdElement):
    # I tried to make the memory fingerprint smaller with this
    # however this does not work with multiple inheritance
    # __slots__ = ()

    def __init__(
        self,
        classes: set=None,
        element_id: str=None,
        input_type='text',
        name: str=None,
        form: str=None,
        value: str=None,
        required=False,
        additional: dict=None
    ):
        super().__init__(
            'input',
            classes=classes,
            element_id=element_id,
            additional=additional
        )
        self._value_params['name'] = name
        self._value_params['type'] = input_type
        self._value_params['form'] = form
        self._value_params['value'] = value
        if required:
            self._params.add('required')

    def render(self):
        return '<{} />'.format(self.render_head())


class TextInput(Input):
    # I tried to make the memory fingerprint smaller with this
    # however this does not work with multiple inheritance
    # __slots__ = ()

    def __init__(
        self,
        classes:set=None,
        element_id:str=None,
        name:str=None,
        form:str=None,
        value:str=None,
        size:int=60,
        required=False,
        additional:dict=None
    ):
        super().__init__(
            classes=classes,
            element_id=element_id,
            input_type='text',
            name=name,
            form=form,
            value=value,
            required=required,
            additional=additional
        )
        self._value_params['size'] = size


class AbstractCheckable(Input):
    # I tried to make the memory fingerprint smaller with this
    # however this does not work with multiple inheritance
    # __slots__ = ()

    def __init__(
        self,
        input_type,
        classes:set=None,
        element_id:str=None,
        name:str=None,
        form:str=None,
        value:str=None,
        required=False,
        checked=False,
        additional:dict=None
    ):
        super().__init__(
            classes=classes,
            element_id=element_id,
            input_type=input_type,
            name=name,
            form=form,
            value=value,
            required=required,
            additional=additional
        )
        if checked:
            self._value_params['checked'] = 'checked'


Radio = functools.partial(AbstractCheckable, input_type='radio')
Checkbox = functools.partial(AbstractCheckable, input_type='checkbox')


class Textarea(ContainerElement):
    # I tried to make the memory fingerprint smaller with this
    # however this does not work with multiple inheritance
    # __slots__ = ()

    def __init__(
        self,
        *content,
        classes:set=None,
        element_id:str=None,
        name:str=None,
        form:str=None,
        required=False,
        rows=0,
        cols=0,
        additional:dict=None
    ):
        super().__init__(
            *content,
            html_type='textarea',
            classes=classes,
            element_id=element_id,
            additional=additional)
        self._value_params['name'] = name
        self._value_params['form'] = form
        self._value_params['rows'] = rows
        self._value_params['cols'] = cols
        if required:
            self._params.add('required')


class Label(ContainerElement):
    # I tried to make the memory fingerprint smaller with this
    # however this does not work with multiple inheritance
    # __slots__ = ()

    def __init__(
        self,
        *content,
        label_for:str=None,
        classes:set=None,
        element_id:str=None,
        additional:dict=None
    ):
        super().__init__(
            *content,
            html_type='label',
            classes=classes,
            element_id=element_id,
            additional=additional
        )
        self._value_params['label'] = label_for


def SubmitButton(
    value='Submit',
    classes:set=None,
    element_id:str=None,
    name:str=None,
    form:str=None,
    additional:dict=None
):
    return Input(
        value=value,
        classes=classes,
        element_id=element_id,
        name=name,
        input_type='submit',
        form=form,
        additional=additional
    )


class FormElement(ContainerElement):
    # I tried to make the memory fingerprint smaller with this
    # however this does not work with multiple inheritance
    # __slots__ = 'submit',

    def __init__(
        self,
        *content,
        action='<?dchp echo(request.url) ?>',
        classes:set=None,
        element_id:str=None,
        method='post',
        charset='UTF-8',
        submit=SubmitButton(),
        target:str=None,
        additional:dict=None
    ):
        super().__init__(
            *content,
            html_type='form',
            classes=classes,
            element_id=element_id,
            additional=additional
        )
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


# HACK 'defaultdict' esque hack to provide all elements to the parser
# SECURITY ISSUE! Template will not be checked for html correctness
class Elements(dict):
    __slots__ = ()

    def __getitem__(self, item):
        if item in self:
            return super().__getitem__(item)
        else:
            return functools.partial(ContainerElement, html_type=item)


# TODO add all elements
elements = Elements(
    a=functools.partial(A, '/'),
    span=Span,
    div=Div,
    html=HTMLPage,
    head=functools.partial(ContainerElement, html_type='head'),
    body=functools.partial(ContainerElement, html_type='body'),
    form=FormElement,
    label=Label
)
