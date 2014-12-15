from http import cookies
from dynct.core.mvc import model as _model
from dynct.errors import html_message
from dynct.modules.comp import html


__author__ = 'justusadam'


class ContentCompiler:
    def compile(self):
        return ''

    def __str__(self):
        return str(self.compile())


class ModelBasedContentCompiler(ContentCompiler):
    _theme = 'default_theme'

    view_name = ''

    def __init__(self, model):
        super().__init__()
        self._model = model
        self._model.theme = self.theme

    @property
    def theme(self):
        return self._theme

    def compile(self):
        self._fill_model()
        return 'page'

    def _fill_model(self):
        pass


class Content(ModelBasedContentCompiler):
    theme = 'default_theme'
    view_name = 'page'
    page_title = 'Dynamic Page'
    permission = 'access pages'
    published = True
    permission_for_unpublished = 'access unpublished pages'

    def __init__(self, model):
        super().__init__(model)
        self._cookies = None

    @property
    def cookies(self):
        if not self._cookies:
            self._cookies = cookies.SimpleCookie()
        return self._cookies

    @property
    def client(self):
        return self._model.client

    def process_content(self):
        pass

    def editorial(self):
        l = self.editorial_list()
        if l:
            return html.List(
                *[html.ContainerElement(name, html_type='a', classes={'editorial-link'}, additional={'href': link}) for
                  name, link in l],
                classes={'editorial-list'}
            )
        return ''

    def editorial_list(self):
        return []

    def _fill_model(self):
        self._model['editorial'] = self.editorial()
        self._model['content'] = self.process_content()
        self._model['title'] = self.page_title

    def check_own_permission(self):
        if not self.published:
            if not self.check_permission(self.permission_for_unpublished):
                return False
        return self.check_permission(self.permission)

    def check_permission(self, permission):
        return self.client.check_permission(permission)

    def compile(self):
        if self.check_own_permission():
            model = super().compile()
            if self.cookies:
                model.cookies = self.cookies
            c = model
        else:
            c = _model.Model('page', content=str(html_message.error_message(401)))
        return c