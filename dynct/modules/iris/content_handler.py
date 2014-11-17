from urllib import parse
from urllib.error import HTTPError

from dynct.core import Modules
from dynct.core.mvc.content_compiler import Content
from dynct.core.mvc.controller import Controller
from dynct.modules.comp.html_elements import FormElement, TableElement, Label, ContainerElement, Checkbox, A, TableRow, TextInput
from dynct.modules.wysiwyg import decorator_hook
from dynct.util.url import UrlQuery, Url
from dynct.core.ar import ContentTypes
from dynct.errors import InvalidInputError
from dynct.modules.commons.menus import menu_chooser, root_ident
from dynct.modules.commons.ar import MenuItem
from . import ar


__author__ = 'justusadam'

_access_modifier = 'access'
_edit_modifier = 'edit'
_add_modifier = 'add'

_publishing_flag = 'published'

_step = 5

_scroll_left = '<'
_scroll_right = '>'

def not_over(a, val):
    if a > val:
        return val
    else:
        return a
def not_under(a, val=0):
    if a < val:
        return val
    else:
        return a


def wrap_compiler(class_):
    def wrapped(*args, **kwargs):
        return class_(*args, **kwargs).compile()

    return wrapped


class FieldBasedPageContent(Content):
    modifier = _access_modifier
    _editorial_list_base = edits = [('edit', _edit_modifier)]

    def __init__(self, url, client, cut_content=False):
        super().__init__(client)
        self.url = url
        self.cut_content = cut_content
        self.modules = Modules()
        self.page = self.get_page()
        self._theme = ContentTypes.get(content_type_name=self.page.content_type).theme
        self.fields = self.get_fields()
        self.permission = self.join_permission(self.modifier, self.page.content_type)
        self.permission_for_unpublished = self.join_permission('access unpublished', self.page.content_type)

    def get_page(self):
        return ar.page(self.url.page_type).get(id=self.url.page_id)

    @property
    def page_title(self):
        return self.page.page_title

    def join_permission(self, modifier, content_type):
        return ' '.join([modifier, 'content type', content_type])

    def get_fields(self):
        field_info = ar.FieldConfig.get_all(content_type=self.page.content_type)

        return [self.get_field_handler(a.machine_name, a.handler_module) for a in field_info]

    def handle_single_field_post(self, field_handler):
        query_keys = field_handler.get_post_query_keys()
        if query_keys:
            vals = {}
            for key in query_keys:
                if key in self.url.post:
                    vals[key] = self.url.post[key]
            if vals:
                field_handler.process_post(UrlQuery(vals))

    def handle_single_field_get(self, field_handler):
        query_keys = field_handler.get_post_query_keys()
        if query_keys:
            vals = {}
            for key in query_keys:
                if key in self.url.get_query:
                    vals[key] = self.url.post[key]
            if vals:
                field_handler.process_get(UrlQuery(vals))

    def get_field_handler(self, name, module):
        return self.modules[module].field_handler(name, self.url.page_type, self.url.page_id, self.modifier)

    def concatenate_content(self, fields):
        content = self.field_content(fields)
        return ContainerElement(*content)

    def field_content(self, fields):
        content = []
        for field in fields:
            content.append(field.compile().content)
        return content

    def process_content(self):
        return self.concatenate_content(self.fields)

    def editorial_list(self):
        s = []
        for (name, modifier) in self._editorial_list_base:
            if self.check_permission(self.join_permission(modifier, self.page.content_type)):
                s.append((name, '/'.join(['', self.url.page_type, str(self.url.page_id), modifier])))
        return s


class EditFieldBasedContent(FieldBasedPageContent):
    modifier = _edit_modifier
    _editorial_list_base = [('show', _access_modifier)]
    field_identifier_separator = '-'
    theme = 'admin_theme'

    def __init__(self, url, client):
        super().__init__(url, client)
        self.menu_item = MenuItem.get_all(item_path=self.url.path.prt_to_str(0, -1))
        if self.menu_item:
            self.menu_item = self.menu_item[0]

    @property
    def page_title(self):
        return ' '.join([self.modifier, self.page.content_type, 'page'])

    @property
    def title_options(self):
        return [Label('Title', label_for='edit-title'),
                TextInput(element_id='edit-title', name='title', value=self.page.page_title, required=True, size=100)]

    def concatenate_content(self, fields):
        content = [self.title_options]
        content += self.field_content(fields)
        table = TableElement(*content, classes={'edit', self.page.content_type, 'edit-form'})
        return FormElement(table, self.admin_options(), action=str(self.url))

    def field_content(self, fields):
        content = []
        for field in fields:
            identifier = self.make_field_identifier(field.machine_name)
            c_fragment = field.compile()
            c_fragment.content.classes.add(self.page.content_type)
            c_fragment.content.element_id = identifier
            content.append((Label(field.machine_name, label_for=identifier), str(c_fragment.content)))
        return content

    def make_field_identifier(self, name):
        return self.modifier + self.field_identifier_separator + name

    def admin_options(self):
        if self.menu_item:
            parent = {False: self.menu_item.parent_item, True: str(-1)}[self.menu_item.parent_item is None]
            selected = '-'.join([self.menu_item.menu, str(parent)])
            m_c = menu_chooser('parent-menu', selected=selected)
        else:
            m_c = menu_chooser('parent-menu')
        menu_options = TableRow(
            Label('Menu Parent', label_for='parent-menu') , m_c, classes={'menu-parent'})
        publishing_options = TableRow(
            Label('Published', label_for='toggle-published'),
               Checkbox(element_id='toggle-published', value=_publishing_flag, name=_publishing_flag,
                        checked=self.published), classes={'toggle-published'})

        return TableElement(publishing_options, menu_options, classes={'admin-options'})

    def process_fields(self, fields):
        for field in fields:
            field.process_post()

    def assign_inputs(self, fields):
        for field in fields:
            mapping = {}
            for key in field.post_query_keys:
                if not key in self.url.post:
                    raise KeyError
                mapping[key] = [parse.unquote_plus(a) for a in self.url.post[key]]
            field.query = mapping

    def process_page(self):
        if not 'title' in self.url.post:
            raise ValueError
        self.page.page_title = parse.unquote_plus(self.url.post['title'][0])
        if _publishing_flag in self.url.post:
            published = True
        else:
            published = False
        self.page.published = published
        self.page.save()
        if 'parent-menu' in self.url.post:
            if self.url.post['parent-menu'][0] == 'none':
                if self.menu_item:
                    self.menu_item.delete()
            else:
                menu_name, parent = self.url.post['parent-menu'][0].split('-', 1)
                if parent == str(root_ident):
                    parent = None
                if self.menu_item:
                    self.menu_item.parent_item = parent
                    self.menu_item.menu = menu_name
                else:
                    self.menu_item = MenuItem(self.page_title,
                                 self.url.path.prt_to_str(0,1) + '/' + str(self.url.page_id),
                                 menu_name,
                                 True,
                                 parent,
                                 10)
                self.menu_item.save()
        return self.url.path.prt_to_str(0,1) + '/' + str(self.url.page_id)

    def _process_post(self):
        self.assign_inputs(self.fields)
        try:
            page = self.process_page()
            self.process_fields(self.fields)
            self.redirect(page)
        except ValueError:
            pass

    def compile(self):
        if self.url.post:
            self._process_post()
        c = super().compile()
        decorator_hook(c)
        return c

    def redirect(self, destination=None):
        if 'destination' in self.url.get_query:
            destination = self.url.get_query['destination'][0]
        elif not destination:
            destination = str(self.url.path.prt_to_str(0, -1))
        raise HTTPError(str(self.url), 302, 'Redirect',
                        {('Location', destination), ('Connection', 'close')}, None)


class AddFieldBasedContentHandler(EditFieldBasedContent):
    modifier = 'add'

    def get_page(self):
        if 'ct' in self.url.get_query:
            content_type = self.url.get_query['ct'][0]
        elif len(self.url.path) == 3:
            content_type = self.url.path[2]
        else:
            raise InvalidInputError
        display_name = ContentTypes.get(content_type_name=content_type).display_name
        title = 'Add new ' + display_name + ' page'
        return ar.page(self.url.page_type)(content_type, title, self.client.user, True)

    def process_page(self):
        self.page.page_title = parse.unquote_plus(self.url.post['title'][0])
        if _publishing_flag in self.url.post:
            self.page.published = True
        else:
            self.page.published = True
        self.page.save()
        page_id = self.page.get_id()
        self.update_field_page_id(page_id)
        self.url.page_id = page_id
        return self.url.path.prt_to_str(0,1) + '/' + str(self.url.page_id)

    def update_field_page_id(self, page_id):
        for field in self.fields:
            field.page_id = page_id

    @property
    def title_options(self):
        return [Label('Title', label_for='edit-title'), TextInput(element_id='edit-title', name='title', size=100, required=True)]


class Overview(Content):
    def __init__(self, url, client):
        super().__init__(client)
        self.url = url
        self.page_title = 'Overview'
        self.permission = ' '.join(['access', self.url.page_type, 'overview'])

    def get_range(self):
        acc = []
        if 'from' in self.url.get_query:
            acc.append(int(self.url.get_query['from'][0]))
        else:
            acc.append(0)
        if 'to' in self.url.get_query:
            acc.append(int(self.url.get_query['to'][0]))
        else:
            acc.append(_step)
        return acc

    def max(self):
        return ar.page(self.url.page_type).get_many('1', 'id desc')[0].id

    def scroll(self, range):
        acc = []
        if not range[0] <= 0:
            after = not_under(range[0] - 1, 0)
            before = not_under(range[0] - _step, 0)
            acc.append(A(''.join([str(self.url.path), '?from=', str(before), '&to=', str(after)]), _scroll_left, classes={'page-tabs'}))
        maximum = self.max()
        if not range[1] >= maximum:
            before = not_over(range[1] + 1, maximum)
            after = not_over(range[1] + _step, maximum)
            acc.append(A(''.join([str(self.url.path), '?from=', str(before), '&to=', str(after)]), _scroll_right, classes={'page-tabs'}))
        return ContainerElement(*acc)

    def process_content(self):
        range = self.get_range()
        pages = []
        for a in ar.page(self.url.page_type).get_many(','.join([str(a) for a in [range[0], range[1] - range[0] + 1]]), 'date_created desc'):
            u = Url(str(self.url.path) + '/' + str(a.id))
            u.page_type = self.url.page_type
            u.page_id = str(a.id)
            pages.append(FieldBasedPageContent(u, self.client))
        content = [ContainerElement(A(str(b.url.path), ContainerElement(b.page_title, html_type='h2')), ContainerElement(b.compile()['content'])) for b in pages]
        content.append(self.scroll(range))
        return ContainerElement(*content)


class IrisController(Controller):
    handler_map = {
        _access_modifier: FieldBasedPageContent,
        _edit_modifier: EditFieldBasedContent,
        _add_modifier: AddFieldBasedContentHandler,
        'overview': Overview
    }

    def __init__(self):
        super().__init__(iris=self.handle)

    def handle(self, url, client):
        if len(url.path) == 3:
            if not url.path[1].isdigit():
                if url.path[1] == _add_modifier:
                    page_modifier = _add_modifier
                    url.page_id = 0
                else:
                    raise InvalidInputError
            else:
                url.page_id = int(url.path[1])
                page_modifier = url.path[2]
        elif len(url.path) == 2:
            if url.path[1].isdigit():
                url.page_id = int(url.path[1])
                page_modifier = _access_modifier
            else:
                if not url.path[1] == _add_modifier:
                    raise InvalidInputError
                page_modifier = _add_modifier
                # This is dirty and should not be done this way
                url.page_id = 0
        elif len(url.path) == 1:
            page_modifier = 'overview'
            url.page_type = url.path[0]
        else:
            raise InvalidInputError
        url.page_type = url.path[0]
        return self.handler_map[page_modifier](url, client).compile()