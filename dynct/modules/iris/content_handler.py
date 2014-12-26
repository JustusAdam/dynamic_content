import functools
from urllib import parse

from dynct import core
from dynct.core.mvc import content_compiler as _cc, decorator as mvc_dec, model as mvc_model
from dynct.modules.comp import decorator as comp_dec
from dynct.modules.comp import html
from dynct.modules.iris import node as _node
from dynct.util import url as _url
from dynct.core import model as coremodel
from dynct.modules.commons import menus as _menus, model as commons_model
from . import model as _model, decorator, node as _nodemodule


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


@core.Component('IrisCompilers')
class Compilers(dict):
    def __init__(self):
        cts = coremodel.ContentTypes.select()
        cts = {ct.machine_name: FieldBasedPageContent(ct) for ct in cts}
        super().__init__(**cts)

    def __getitem__(self, item):
        if isinstance(item, coremodel.ContentTypes):
            item = item.machine_name
        return super().__getitem__(item)

    def __setitem__(self, key, value):
        if isinstance(key, coremodel.ContentTypes):
            key = key.machine_name
        return super().__setitem__(key, value)


class FieldBasedPageContent(object):
    _editorial_list_base = edits = [('edit', _edit_modifier)]
    _view_name = 'page'
    page_type = 'iris'

    def __init__(self, content_type):
        self.dbobj = content_type
        self.content_type = content_type.machine_name
        self.fields = self.get_fields()
        self.modules = core.Modules
        self.theme = self.dbobj.theme

    def get_permission(self, page, modifier):
        return self.join_permission(modifier) if page.published else \
            self.join_permission('access unpublished')

    def compile(self, model, page, modifier, pre_compile_hook=None, post_compile_hook=None, content_compiler_hook=None):

        model.client.check_permission(self.get_permission(page, modifier))

        pre_compile_hook() if pre_compile_hook else None

        node = _nodemodule.Node(
            editorial=self.editorial(page, model.client),
            content=content_compiler_hook(page) if content_compiler_hook else self.concatenate_content(page),
            title=page.page_title)

        post_compile_hook() if post_compile_hook else None

        return node

    def access(self, model, page):
        return self.compile(model, page, 'access')

    def edit(self, model, page):
        return self.compile(model, page, 'edit', content_compiler_hook=functools.partial(self.edit_form, self))

    def process_edit(self, model, page, post):
        model.client.check_permission(self.get_permission(page, 'add'))

        success = True
        return ':redirect:/iris/' + str(page.oid) + ('' if success else '/add')

    def add(self):
        pass

    def edit_form(self, page):
        content = [self.title_options(page)]
        content += self.field_content(page)
        table = html.TableElement(*content, classes={'edit', page.content_type, 'edit-form'})
        return html.FormElement(table, self.admin_options(page), action='/iris/' + str(page.oid) + '/edit')

    def editorial(self, page, client):
        l = self.editorial_list(page, client)
        if l:
            return html.List(
                *[html.ContainerElement(name, html_type='a', classes={'editorial-link'}, additional={'href': link}) for
                  name, link in l],
                classes={'editorial-list'}
            )
        else:
            return ''

    def join_permission(self, modifier):
        return ' '.join([modifier, 'content type', self.content_type])

    def get_fields(self):
        field_info = _model.FieldConfig.get_all(_model.FieldConfig.content_type==self.content_type)
        for a in field_info:
            yield self.get_field_handler(a.machine_name, a.handler_module)

    def get_field_handler(self, name, module):
        return self.modules[module].field_handler(name, self.page_type)

    def concatenate_content(self, page):
        content = self.field_content(page)
        return html.ContainerElement(*content)

    def field_content(self, page):
        for field in self.fields:
            yield field(page)

    def editorial_list(self, page, client):
        for (name, modifier) in self._editorial_list_base:
            if client.check_permission(self.join_permission(modifier)):
                yield (name, '/'.join(['', self.page_type, str(page.oid), modifier]))

    def admin_options(self, page):
        if page.menu_item:
            parent = '-1' if page.menu_item.parent_item is None else page.menu_item.parent_item
            selected = '-'.join([page.menu_item.menu, str(parent)])
            m_c = _menus.menu_chooser('parent-menu', selected=selected)
        else:
            m_c = _menus.menu_chooser('parent-menu')
        menu_options = html.TableRow(
            html.Label('Menu Parent', label_for='parent-menu') , m_c, classes={'menu-parent'})
        publishing_options = html.TableRow(
            html.Label('Published', label_for='toggle-published'),
               html.Checkbox(element_id='toggle-published', value=_publishing_flag, name=_publishing_flag,
                        checked=page.published), classes={'toggle-published'})

        return html.TableElement(publishing_options, menu_options, classes={'admin-options'})

    def title_options(self, page):
        return [html.Label('Title', label_for='edit-title'),
                html.TextInput(element_id='edit-title', name='title', value=page.page_title, required=True, size=100)]


@mvc_dec.controller_function('iris', '/([0-9]+)/?(access)?', get=False, post=False)
@comp_dec.Regions
@decorator.node_process
def handle_compile(model, page_id, modifier):
    page = _model.Page.get(oid=page_id)
    modifiers = {

    }
    return getattr(core.get_component('IrisCompilers')[page.content_type], modifiers.get(modifier, modifier))(model, page)


@mvc_dec.controller_function('iris', '/([0-9]+)/edit', get=False, post=True)
def handle_edit(model, page_id, post):
    page = _model.Page.get(oid=page_id)
    return core.get_component('IrisCompilers')[page.content_type.machine_name].process_edit(model, page_id, post)


class EditFieldBasedContent(FieldBasedPageContent):
    modifier = _edit_modifier
    _editorial_list_base = [('show', _access_modifier)]
    field_identifier_separator = '-'

    def __init__(self, content_type):
        super().__init__(content_type)
        self.theme = 'admin_theme'

    def title_options(self, page):
        return [html.Label('Title', label_for='edit-title'),
                html.TextInput(element_id='edit-title', name='title', value=page.page_title, required=True, size=100)]

    def concatenate_content(self, page):
        content = [self.title_options(page)]
        content += self.field_content(page)
        table = html.TableElement(*content, classes={'edit', page.content_type, 'edit-form'})
        return html.FormElement(table, self.admin_options(), action=str(self.url))

    def field_content(self, fields):
        for field in fields:
            identifier = self.make_field_identifier(field.machine_name)
            c_fragment = field.compile()
            c_fragment.content.classes.add(self.page.content_type)
            c_fragment.content.element_id = identifier
            yield html.Label(field.machine_name, label_for=identifier), str(c_fragment.content)

    def make_field_identifier(self, name):
        return self.modifier + self.field_identifier_separator + name

    def admin_options(self):
        if self.menu_item:
            parent = {False: self.menu_item.parent_item, True: str(-1)}[self.menu_item.parent_item is None]
            selected = '-'.join([self.menu_item.menu, str(parent)])
            m_c = _menus.menu_chooser('parent-menu', selected=selected)
        else:
            m_c = _menus.menu_chooser('parent-menu')
        menu_options = html.TableRow(
            html.Label('Menu Parent', label_for='parent-menu') , m_c, classes={'menu-parent'})
        publishing_options = html.TableRow(
            html.Label('Published', label_for='toggle-published'),
               html.Checkbox(element_id='toggle-published', value=_publishing_flag, name=_publishing_flag,
                        checked=self.published), classes={'toggle-published'})

        return html.TableElement(publishing_options, menu_options, classes={'admin-options'})

    def __call__(self, model, page, post, get, *args, **kwargs):
        return self.compile(model, page)


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
                if parent == str(_menus.root_ident):
                    parent = None
                if self.menu_item:
                    self.menu_item.parent_item = parent
                    self.menu_item.menu = menu_name
                else:
                    self.menu_item = commons_model.MenuItem(self.page_title,
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


class AddFieldBasedContentHandler(EditFieldBasedContent):
    modifier = 'add'

    def get_page(self):
        if 'ct' in self.url.get_query:
            content_type = self.url.get_query['ct'][0]
        elif len(self.url.path) == 3:
            content_type = self.url.path[2]
        else:
            raise TypeError
        display_name = coremodel.ContentTypes.get(content_type_name=content_type).display_name
        title = 'Add new ' + display_name + ' page'
        return _model.Page(content_type= content_type, title=title, creator=self.client.user)

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

    def title_options(self):
        return [html.Label('Title', label_for='edit-title'), html.TextInput(element_id='edit-title', name='title', size=100, required=True)]


class Overview(_cc.Content):
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
        return _model.Page.select().order_by('id desc').limit(1).oid

    def scroll(self, range):
        acc = []
        if not range[0] <= 0:
            after = not_under(range[0] - 1, 0)
            before = not_under(range[0] - _step, 0)
            acc.append(html.A(''.join([str(self.url.path), '?from=', str(before), '&to=', str(after)]), _scroll_left, classes={'page-tabs'}))
        maximum = self.max()
        if not range[1] >= maximum:
            before = not_over(range[1] + 1, maximum)
            after = not_over(range[1] + _step, maximum)
            acc.append(html.A(''.join([str(self.url.path), '?from=', str(before), '&to=', str(after)]), _scroll_right, classes={'page-tabs'}))
        return html.ContainerElement(*acc)

    def process_content(self):
        range = self.get_range()
        def pages():
            for a in _model.Page.select().limit(','.join([str(a) for a in [range[0], range[1] - range[0] + 1]])).order_by( 'date_created desc'):
                u = _url.Url(str(self.url.path) + '/' + str(a.id))
                u.page_type = self.url.page_type
                u.page_id = str(a.id)
                m = mvc_model.Model()
                FieldBasedPageContent(m, u).compile()
                yield u, m
        content = [html.ContainerElement(html.A(str(a.path), html.ContainerElement(b['page_title'], html_type='h2')), html.ContainerElement(b['content'])) for a, b in pages()]
        content.append(self.scroll(range))
        return html.ContainerElement(*content)


@mvc_dec.controller_function('iris', '$', post=False)
@comp_dec.Regions
@decorator.node_process
def overview(page_model, get):
    page_model.client.check_permission(' '.join(['access', 'iris', 'overview']))
    my_range = [
            int(get['from'][0]) if 'from' in get else 0,
            int(get['to'][0])   if 'to'   in get else _step
        ]
    for a in _model.Page.select().limit(','.join([str(a) for a in [my_range[0], my_range[1] - my_range[0] + 1]])).order_by('date_created desc'):
        node = _node.access_node(page_model, 'iris', a.oid)
        node['title'] = html.A('/iris/' + str(a.oid), node['title'])
        yield node
