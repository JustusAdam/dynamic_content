import functools

from dyc import core
from dyc.core import mvc
from dyc import dchttp

from dyc.util import lazy, html
from dyc.modules import wysiwyg
from dyc.modules.commons import menus as _menus
from dyc.modules.users import decorator as user_dec
from . import model as _model, field
from .node import node


__author__ = 'Justus Adam'

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


@core.Component('CMSCompilers')
class Compilers(lazy.Loadable):
    def __init__(self):
        self._dict = None
        super().__init__()

    @lazy.ensure_loaded
    def __getitem__(self, item):
        if isinstance(item, _model.ContentTypes):
            item = item.machine_name
        return self._dict[item]

    def load(self):
        self._dict = {ct.machine_name: FieldBasedPageContent(ct) for ct in _model.ContentTypes.select()}


class FieldBasedPageContent(object):
    _editorial_list_base = edits = (('edit', _edit_modifier), )
    _view_name = 'page'
    page_type = 'node'

    def __init__(self, content_type):
        self.dbobj = content_type
        self.content_type = content_type.machine_name
        self.fields = list(self.get_fields())
        self.theme = self.dbobj.theme

    def get_permission(self, page, modifier):
        return self.join_permission(modifier) if page.published else \
            self.join_permission('access unpublished')

    def compile(self, model, page, modifier):

        def _():
            raise TypeError(modifier)

        mapped = {
            _access_modifier : self.field_contents,
            _edit_modifier : self.edit_form,
            _add_modifier : self.add_form
            }

        if not model.client.check_permission(self.get_permission(page, modifier)):
            return None

        node = dict(
            editorial=self.editorial(page, model.client),
            content=mapped.get(modifier, _)(page),
            title=page.page_title
            )


        return node

    def field_contents(self, page):
        return ''.join(str(a) for a in self.field_display(page))

    def field_display(self, page):
        f = lambda a: a['content']
        for single_field in self.fields:
            yield f(single_field.access(page))

    def field_edit(self, page):
        for single_field in self.fields:
            a = single_field.edit(page)
            yield html.Label(a['name'], label_for=a['name'])
            yield a['content']

    def field_add(self):
        for single_field in self.fields:
            a = single_field.add()
            yield html.Label(a['name'], label_for=a['name'])
            yield a['content']

    def access(self, model, page):
        return self.compile(model, page, _access_modifier)

    @wysiwyg.use()
    def edit(self, model, page):
        return self.compile(model, page, _edit_modifier)

    def process_edit(self, model, page, post):
        if not model.client.check_permission(self.get_permission(page, 'add')):
            return None
        try:
            for one_field in self.fields:
                if one_field.config.field_type.machine_name not in post:
                    raise ValueError
            for one_field in self.fields:
                one_field.process_edit(page.oid, post[one_field.config.field_type.machine_name])
            success = True
        except Exception as e:
            print(e)
            success = False

        return ':redirect:/node/' + str(page.oid) + ('' if success else '/add')

    @wysiwyg.use()
    def add(self, model):
        pass

    def add_form(self, page):
        content = self.title_options() + tuple(self.field_add())
        return html.FormElement(*content + (self.admin_options(), ), action='/node/add', classes={'edit', self.content_type, 'edit-form'})

    def edit_form(self, page):
        content = self.title_options(page) + tuple(self.field_edit(page))
        return html.FormElement(*content + (self.admin_options(page), ), action='/node/' + str(page.oid) + '/edit', classes={'edit', self.content_type, 'edit-form'})

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
        field_info = _model.FieldConfig.select().where(_model.FieldConfig.content_type == self.dbobj)
        for a in field_info:
            yield field.Field(a, self.page_type)

    def editorial_list(self, page, client):
        for (name, modifier) in self._editorial_list_base:
            if client.check_permission(self.join_permission(modifier)):
                yield (name, '/'.join(['', self.page_type, str(page.oid), modifier]))

    @staticmethod
    def admin_options(page=None):
        if page is not None and page.menu_item:
            parent = '-1' if page.menu_item.parent_item is None else page.menu_item.parent_item
            selected = '-'.join([page.menu_item.menu, str(parent)])
            m_c = _menus.menu_chooser('parent-menu', selected=selected)
        else:
            m_c = _menus.menu_chooser('parent-menu')
        menu_options = html.TableRow(
            html.Label('Menu Parent', label_for='parent-menu'), m_c, classes={'menu-parent'})
        publishing_options = html.TableRow(
            html.Label('Published', label_for='toggle-published'),
            html.Checkbox(element_id='toggle-published', value=_publishing_flag, name=_publishing_flag,
                          checked=page.published), classes={'toggle-published'})

        return html.TableElement(publishing_options, menu_options, classes={'admin-options'})

    @staticmethod
    def title_options(page=None):
        input_element = functools.partial(
            html.TextInput,
            element_id='edit-title',
            name='title',
            required=True,
            size=90
            )
        return (html.Label('Title', label_for='edit-title'),
                input_element() if page is None else input_element(value=page.page_title))


@mvc.controller_class
@core.inject('CMSCompilers')
class CMSController(object):

    def __init__(self, compiler_map):
        self.compiler_map = compiler_map

    @mvc.controller_method({'/node/{int}', 'node/{int}/access'}, method=dchttp.RequestMethods.GET, query=False)
    @node
    def handle_compile(self, model, page_id):
        page = _model.Page.get(oid=page_id)
        return self.compiler_map[page.content_type].access(model, page)


    @mvc.controller_method('/node/{int}/edit', method=dchttp.RequestMethods.POST, query=True)
    def handle_edit(self, model, page_id, post):
        page = _model.Page.get(oid=page_id)
        return self.compiler_map[page.content_type.machine_name].process_edit(model, page, post)


    @mvc.controller_method('/node/{int}/edit', method=dchttp.RequestMethods.GET, query=False)
    @node
    def handle_edit_page(self, model, page_id):
        page = _model.Page.get(oid=page_id)
        return self.compiler_map[page.content_type.machine_name].edit(model, page)


    @mvc.controller_method('/node', method=dchttp.RequestMethods.GET, query=True)
    @user_dec.authorize(' '.join(['access', 'node', 'overview']))
    @node
    def overview(self, page_model, get):
        my_range = [
            int(get['from'][0]) if 'from' in get else 0,
            int(get['to'][0]) if 'to' in get else _step
        ]
        for a in _model.Page.select().limit(
                ','.join([str(a) for a in [my_range[0], my_range[1] - my_range[0] + 1]])).order_by('date_created desc'):
            node = self.compiler_map[a.content_type.machine_name].access(page_model, a)
            node['title'] = html.A('/node/' + str(a.oid), node['title'])
            yield node

    @mvc.controller_method('/node/add/{str}', method=dchttp.RequestMethods.GET, query=False)
    def add(self, model, content_type):
        return self.compiler_map[content_type].add()