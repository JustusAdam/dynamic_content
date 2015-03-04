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

    def __init__(self, html_type, additional: dict=None):
        self.html_type = html_type
        if additional:
            self._value_params = dict(additional)
        else:
            self._value_params = {}
        self._params = set()

    @property
    def params(self):
        """
        Public accessor for the _params list

        :return: self._params
        """
        return self._params

    @property
    def value_params(self):
        """
        Public accessor for the _value_params dict

        :return: self._value_params
        """
        return self._value_params

    def __add__(self, other):
        return str(self) + str(other)

    def render_head(self):
        """
        Render the inside of the opening tag

        :return: str
        """
        return transform.to_html_head(
            self.html_type,
            self._value_params,
            self._params
        )

    def render(self):
        """
        Return a html representation of this object

        :return: html formatted string
        """
        return '<{}>'.format(self.render_head())

    def __str__(self):
        return self.render()

    def to_iter(self):
        """
        Return self and content as an iterable pf strings

        :return: generator(str)
        """
        return self.render()


class BaseClassIdElement(BaseElement):
    """
    Html base element with classes and id's
    """
    # I tried to make the memory fingerprint smaller with this
    # however this does not work with multiple inheritance
    # __slots__ = ()

    def __init__(
            self,
            html_type,
            classes: set=None,
            element_id: str=None,
            additional: dict=None
        ):
        super().__init__(html_type, additional)
        self._value_params['class'] = classes
        self._value_params['id'] = element_id

    @property
    def classes(self):
        """
        Convenience method for accessing the classes of this element

        :return: iterable of strings
        """
        return self._value_params['class']

    @classes.setter
    def classes(self, val):
        """
        Convenience setter for classes

        :param val: value to set classes to
        :return: None
        """
        self._value_params['class'] = val

    @property
    def element_id(self):
        """
        Convenience method for accessing the elements id

        :return: string
        """
        return self._value_params['id']

    @element_id.setter
    def element_id(self, val):
        """
        Convenience setter for the element id
        :param val:
        :return:
        """
        assert isinstance(val, str)
        self._value_params['id'] = val


class ContainerElement(list, BaseClassIdElement):
    """
    Html base element with other content within
    """
    # I tried to make the memory fingerprint smaller with this
    # however this does not work with multiple inheritance
    # __slots__ = ()

    _list_replacement = None

    def __init__(
            self,
            *content,
            html_type='div',
            classes: set=None,
            element_id: str=None,
            additional: dict=None
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
        """
        Compatibility method for legacy API

        :return: list of content (self)
        """
        return self

    @property
    def list_replacement(self):
        """
        Accessor for list_replacement
        :return: some subclass of BaseElement
        """
        return (
            self._list_replacement
            if self._list_replacement is not None
            else ContainerElement
        )

    def ensure_type(self, value):
        """
        Transform non-dict and non-string iterables as a html element

        :param value: value to transform
        :return: value or list_replacement(*value)
        """
        if isinstance(value, str) or isinstance(value, dict):
            return value
        if hasattr(value, '__iter__'):
            return self.list_replacement(*value)
        else:
            return value

    def render_content(self):
        """
        Render the content within

        :return: string
        """
        return ''.join(str(a) for a in self)

    def render(self):
        """
        Overwrites parent method to render a closing tag and the content

        :return: html formatted string
        """
        return '<{}>{}</{}>'.format(
            self.render_head(),
            self.render_content(),
            self.html_type
        )

    def iter_content(self):
        """
        Iterate over the content within

        :return: generator(object)
        """
        for a in self.content:
            if hasattr(a, 'to_iter'):
                for b in a.to_iter():
                    yield b
            else:
                yield a

    def to_iter(self):
        """
        Generator for the tags and the content
        :return:
        """
        yield '<{}>'.format(self.render_head())
        for a in self.iter_content():
            yield a
        yield '</{}>'.format(self.html_type)


Div = functools.partial(ContainerElement, html_type='div')

Span = functools.partial(ContainerElement, html_type='span')


class AbstractList(ContainerElement):
    """
    Element containing other objects with special rendering requirements
    """
    # I tried to make the memory fingerprint smaller with this
    # however this does not work with multiple inheritance
    # __slots__ = ()

    _subtypes = 'li',
    _regex = re.compile('<(\w+)')

    def subtype_wrapper(self, *args, **kwargs):
        """
        Wrapper to use for child elements

        :param args:
        :param kwargs:
        :return: instance of BaseElement with *args within
        """
        return ContainerElement(*args, html_type=self._subtypes[0], **kwargs)

    def render_content(self):
        """
        Override parent method to ensure the correct type of all contents within

        :return: html formatted string
        """
        return ''.join(str(self.ensure_subtype(a)) for a in self)

    def ensure_subtype(self, value):
        """
        Ensure the element has the type necessary for children of this element.

        :param value: element to test
        :return: instance of self.subtype_wrapper
        """
        if isinstance(value, str):
            m = self._regex.match(value)
            if m and m.group(1) in self._subtypes:
                return value
            else:
                return self.subtype_wrapper(value)
        elif isinstance(value, BaseElement):
            if value.html_type in self._subtypes:
                return value
            else:
                return self.subtype_wrapper(value)
        elif hasattr(value, '__iter__'):
            return self.subtype_wrapper(*value)
        else:
            return self.subtype_wrapper(value)


class A(ContainerElement):
    """
    html <a> element
    """
    # I tried to make the memory fingerprint smaller with this
    # however this does not work with multiple inheritance
    # __slots__ = ()

    def __init__(
            self,
            *content,
            href='/',
            classes: set=None,
            element_id: str=None,
            additional: dict=None
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
    """
    html <html> element
    """
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
            classes: set=None,
            element_id: str=None,
            additional: dict=None,
            metatags: set=None,
            stylesheets: set=None,
            scripts: set=None
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
        """
        Public accessor for the stylesheets property

        :return: _stylesheets
        """
        return self._stylesheets

    @stylesheets.setter
    def stylesheets(self, val):
        """
        Public setter for the stylesheets property

        :param val: value to set stylesheets to
        :return: None
        """
        if isinstance(val, set):
            self._stylesheets = val
        elif isinstance(val, (list, tuple)):
            self._stylesheets = set(val)
        elif isinstance(val, str):
            self._stylesheets = {val}

    @property
    def metatags(self):
        """
        Public accessor for the metatags property

        :return: _metatags
        """
        return self._metatags

    @metatags.setter
    def metatags(self, val):
        """
        Public setter for metatag property

        :param val: value to set it to
        :return: None
        """
        if isinstance(val, set):
            self._metatags = val
        elif isinstance(val, (list, tuple)):
            self._metatags = set(val)
        elif isinstance(val, str):
            self._metatags = {val}

    @property
    def scripts(self):
        """
        Public accessor for the scripts property

        :return: _scripts
        """
        return self._scripts

    @scripts.setter
    def scripts(self, val):
        """
        Public setter for the scripts property

        :param val: value to set it to
        :return: None
        """
        if isinstance(val, set):
            self._scripts = val
        elif isinstance(val, (list, tuple)):
            self._scripts = set(val)
        elif isinstance(val, str):
            self._scripts = {val}

    def add(self, other):
        """
        Combine two HTMLpage instances into one

        :param other: page to combine it with
        :return: None
        """
        assert isinstance(other, HTMLPage)
        self._stylesheets |= other.stylesheets
        self._metatags |= other.metatags
        self._scripts |= other.scripts
        self.extend(other)


class LinkElement(BaseElement):
    """
    Html link element
    """
    # I tried to make the memory fingerprint smaller with this
    # however this does not work with multiple inheritance
    # __slots__ = ()

    def __init__(
            self,
            href,
            rel,
            element_type: str=None,
            additional: dict=None
        ):
        super().__init__('link', additional)
        self._value_params['rel'] = rel
        self._value_params['href'] = href
        self._value_params['type'] = element_type


class Stylesheet(BaseElement):
    """Html <link rel="stylesheet"> element"""
    # I tried to make the memory fingerprint smaller with this
    # however this does not work with multiple inheritance
    # __slots__ = ()

    def __init__(
            self,
            href,
            media='all',
            typedec='text/css',
            rel='stylesheet',
            additional: dict=None
        ):
        super().__init__('link', additional)
        self._value_params['href'] = href
        self._value_params['media'] = media
        self._value_params['type'] = typedec
        self._value_params['rel'] = rel


class Script(ContainerElement):
    """Html <script> element"""
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
    """html <ul> or <ol> element"""
    # I tried to make the memory fingerprint smaller with this
    # however this does not work with multiple inheritance
    # __slots__ = 'item_classes', 'item_additionals'

    _subtypes = 'li',

    def __init__(
            self,
            *content,
            list_type='ul',
            classes: set=None,
            element_id: str=None,
            additional: dict=None,
            item_classes: set=None,
            item_additional_properties: dict=None
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
        """
        Override parent method to propagate classes

        :param value: value to ensure the type
        :return:
        """
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


Ol = functools.partial(List, list_type='ol')

Ul = functools.partial(List, list_type='ul')


class Select(AbstractList):
    """html <select> element"""
    # I tried to make the memory fingerprint smaller with this
    # however this does not work with multiple inheritance
    # __slots__ = 'selected',

    _subtypes = 'option',

    def __init__(
            self,
            *content,
            classes: set=None,
            element_id: str=None,
            additional: dict=None,
            form: str=None,
            required: bool=False,
            disabled: bool=False,
            name: str=None,
            selected: str=None
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
        """
        Override parent method because of 'selected'

        :param value:
        :param content:
        :return:
        """
        return Option(content, value=value, selected=self.selected == value)


class Option(ContainerElement):
    """html <option> element"""
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
        """
        Override parent to account for 'selected'

        :return: string
        """
        if self.selected:
            return super().render_head() + ' selected'
        else:
            return super().render_head()


class TableElement(ContainerElement):
    """html <table> element"""
    # I tried to make the memory fingerprint smaller with this
    # however this does not work with multiple inheritance
    # __slots__ = 'table_head',

    def __init__(
            self,
            *content,
            classes: set=None,
            element_id: str=None,
            additional: dict=None,
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
        """
        Override parent to accoutn for ht elements

        :return: string
        """
        def compile_c():
            """
            Iter self, ensuring subtype

            :return: generator
            """
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
        """
        Ensure the element is a <tr> element

        :param row: row to check
        :return: TableRow()
        """
        if isinstance(row, ContainerElement) and row.html_type == 'tr':
            return row
        elif isinstance(row, (list, tuple)):
            return TableRow(*row)
        return TableRow(row)

    @staticmethod
    def ensure_th(row):
        """
        Ensure the element is a <th> element

        :param row: row to check
        :return: TableHead()
        """
        if isinstance(row, ContainerElement) and row.html_type == 'th':
            return str(row)
        elif isinstance(row, (list, tuple)):
            return str(TableHead(*row))
        return str(TableHead(row))


Table = TableElement


class AbstractTableRow(AbstractList):
    """
    Abstract base class for table rows
    """
    # I tried to make the memory fingerprint smaller with this
    # however this does not work with multiple inheritance
    # __slots__ = ()

    _subtypes = 'td'

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


Th = TableHead = functools.partial(AbstractTableRow, html_type='th')

Tr = TableRow = functools.partial(AbstractTableRow, html_type='tr')

Td = TableData = functools.partial(ContainerElement, html_type='td')


class Input(BaseClassIdElement):
    """html <input> element"""
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
            html_type='input',
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
        """
        Render with closed tag

        :return: string
        """
        return '<{} />'.format(self.render_head())


class TextInput(Input):
    """html <input type="text"> element"""
    # I tried to make the memory fingerprint smaller with this
    # however this does not work with multiple inheritance
    # __slots__ = ()

    def __init__(
            self,
            classes: set=None,
            element_id: str=None,
            name: str=None,
            form: str=None,
            value: str=None,
            size: int=60,
            required=False,
            additional: dict=None
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
    """html input with 'checked' attribute"""
    # I tried to make the memory fingerprint smaller with this
    # however this does not work with multiple inheritance
    # __slots__ = ()

    def __init__(
            self,
            input_type,
            classes: set=None,
            element_id: str=None,
            name: str=None,
            form: str=None,
            value: str=None,
            required=False,
            checked=False,
            additional: dict=None
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
    """html <textarea> element"""
    # I tried to make the memory fingerprint smaller with this
    # however this does not work with multiple inheritance
    # __slots__ = ()

    def __init__(
            self,
            *content,
            classes: set=None,
            element_id: str=None,
            name: str=None,
            form: str=None,
            required=False,
            rows=0,
            cols=0,
            additional: dict=None
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
    """html <label> element"""
    # I tried to make the memory fingerprint smaller with this
    # however this does not work with multiple inheritance
    # __slots__ = ()

    def __init__(
            self,
            *content,
            label_for: str=None,
            classes: set=None,
            element_id: str=None,
            additional: dict=None
        ):
        super().__init__(
            *content,
            html_type='label',
            classes=classes,
            element_id=element_id,
            additional=additional
        )
        self._value_params['label'] = label_for


SubmitButton = lambda *args, value='Submit', **kwargs: Input(
    *args, value=value, input_type='submit', **kwargs
)


class FormElement(ContainerElement):
    """html <form> element"""
    # I tried to make the memory fingerprint smaller with this
    # however this does not work with multiple inheritance
    # __slots__ = 'submit',

    def __init__(
        self,
        *content,
        action='<?dchp echo(request.url) ?>',
        classes: set=None,
        element_id: str=None,
        method='post',
        charset='UTF-8',
        submit=SubmitButton(),
        target: str=None,
        additional: dict=None
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
        """
        Override parent to add submit element

        :return: string
        """
        return super().render_content() + str(self.submit)


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
