from urllib import parse
from urllib.error import HTTPError

from dynct.core import Modules
from dynct.core.mvc.content_compiler import Content
from dynct.core.mvc.decorator import controller_class, controller_method, controller_function
from dynct.core.mvc.model import Model
from dynct.modules.comp.decorator import Regions
from dynct.modules.comp.html import FormElement, TableElement, Label, ContainerElement, Checkbox, A, TableRow, TextInput
from dynct.modules.iris.node import access_node
from dynct.modules.wysiwyg import decorator_hook
from dynct.util.url import UrlQuery, Url
from dynct.core.model import ContentTypes
from dynct.modules.commons.menus import menu_chooser, root_ident
from dynct.modules.commons.model import MenuItem
from . import model
from .decorator import node_process


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

    def __init__(self, model, url):
        super().__init__(model)
        self.url = url
        self.modules = Modules
        self.page = self.get_page()
        self._theme = self.page.content_type.theme
        self.fields = self.get_fields()
        self.permission = self.join_permission(self.modifier, self.page.content_type)
        self.permission_for_unpublished = self.join_permission('access unpublished', self.page.content_type)

    def get_page(self):
        return model.Page.get(model.Page.oid==self.url.page_id)

    @property
    def page_title(self):
        return self.page.page_title

    def join_permission(self, modifier, content_type):
        return ' '.join([modifier, 'content type', content_type])

    def get_fields(self):
        field_info = model.FieldConfig.get_all(model.FieldConfig.content_type==self.page.content_type)
        for a in field_info:
            yield self.get_field_handler(a.machine_name, a.handler_module)

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
        for (name, modifier) in self._editorial_list_base:
            if self.check_permission(self.join_permission(modifier, self.page.content_type)):
                yield (name, '/'.join(['', self.url.page_type, str(self.url.page_id), modifier]))


class EditFieldBasedContent(FieldBasedPageContent):
    modifier = _edit_modifier
    _editorial_list_base = [('show', _access_modifier)]
    field_identifier_separator = '-'
    theme = 'admin_theme'

    def __init__(self, model, url):
        super().__init__(model, url)
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
        for field in fields:
            identifier = self.make_field_identifier(field.machine_name)
            c_fragment = field.compile()
            c_fragment.content.classes.add(self.page.content_type)
            c_fragment.content.element_id = identifier
            yield Label(field.machine_name, label_for=identifier), str(c_fragment.content)

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
            field.query = {key: [parse.unquote_plus(a) for a in self.url.post[key]] for key in field.post_query_keys}

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
        decorator_hook(self._model)
        return super().compile()

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
            raise TypeError
        display_name = ContentTypes.get(content_type_name=content_type).display_name
        title = 'Add new ' + display_name + ' page'
        return model.Page(content_type= content_type, title=title, creator=self.client.user)

    def process_page(self):
        self.page.page_title = parse.unquote_plus(self.url.post['title'][0])
        self.page.published = _publishing_flag in self.url.post
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
    def __init__(self, model, url):
        super().__init__(model)
        self.url = url
        self.page_title = 'Overview'
        self.permission = ' '.join(['access', self.url.page_type, 'overview'])

    def get_range(self):
        return [
            int(self.url.get_query['from'][0]) if 'from' in self.url.get_query else 0,
            int(self.url.get_query['to'][0])   if 'to'   in self.url.get_query else _step
        ]

    def max(self):
        return model.Page.select().order_by('id desc').limit(1).oid

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
        def pages():
            for a in model.Page.select().limit(','.join([str(a) for a in [range[0], range[1] - range[0] + 1]])).order_by( 'date_created desc'):
                u = Url(str(self.url.path) + '/' + str(a.id))
                u.page_type = self.url.page_type
                u.page_id = str(a.id)
                m = Model()
                FieldBasedPageContent(m, u).compile()
                yield u, m
        content = [ContainerElement(A(str(a.path), ContainerElement(b['page_title'], html_type='h2')), ContainerElement(b['content'])) for a, b in pages()]
        content.append(self.scroll(range))
        return ContainerElement(*content)


@controller_function('iris', '$', post=False)
@Regions
@node_process
def overview(page_model, get):
    page_model.client.check_permission(' '.join(['access', 'iris', 'overview']))
    my_range = [
            int(get['from'][0]) if 'from' in get else 0,
            int(get['to'][0])   if 'to'   in get else _step
        ]
    for a in model.Page.select().limit(','.join([str(a) for a in [my_range[0], my_range[1] - my_range[0] + 1]])).order_by('date_created desc'):
        node = access_node(page_model, 'iris', a.oid)
        node['title'] = A('/iris/' + str(a.oid), node['title'])
        yield node


@controller_class
class IrisController:
    handler_map = {
        _access_modifier: FieldBasedPageContent,
        _edit_modifier: EditFieldBasedContent,
        _add_modifier: AddFieldBasedContentHandler,
    }

    @node_process
    def overview(self, model, url):
        return Overview(model, url).compile()

    @controller_method('iris', '/([1-9]+)/edit', get=False, post=True)
    @node_process
    def edit(self, model, node_id, post):
        pass

    @controller_method('iris')
    @Regions
    def handle(self, model, url, get, post):
        if len(url.path) == 3:
            if not url.path[1].isdigit():
                if url.path[1] == _add_modifier:
                    page_modifier = _add_modifier
                    url.page_id = 0
                else:
                    raise TypeError
            else:
                url.page_id = int(url.path[1])
                page_modifier = url.path[2]
        elif len(url.path) == 2:
            if url.path[1].isdigit():
                url.page_id = int(url.path[1])
                page_modifier = _access_modifier
            else:
                if not url.path[1] == _add_modifier:
                    raise TypeError
                page_modifier = _add_modifier
                # This is dirty and should not be done this way
                url.page_id = 0
        elif len(url.path) == 1:
            page_modifier = 'overview'
            url.page_type = url.path[0]
        else:
            raise TypeError
        url.page_type = url.path[0]
        return self.handler_map[page_modifier](model, url).compile()

@controller_function('iris', '/([1-9]+)(?:/access)?', get=False, post=False)
@Regions
@node_process
def access(model, node_id):
    return access_node(model, 'iris', int(node_id))