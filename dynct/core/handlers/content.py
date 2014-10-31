from dynct.core.handlers.base import WebObject, ModelBasedContentCompiler
from dynct.core.mvc.model import Model
from dynct.errors import html_message
from dynct.modules.comp.html_elements import List, ContainerElement

__author__ = 'justusadam'


class Content(WebObject, ModelBasedContentCompiler):
    theme = 'default_theme'
    view_name = 'page'
    page_title = 'Dynamic Page'
    permission = 'access pages'
    published = True
    permission_for_unpublished = 'access unpublished pages'

    def __init__(self, url, client):
        # assert isinstance(client, ClientInformation)
        super().__init__(url)
        ModelBasedContentCompiler.__init__(self)
        self._client = client

    @property
    def client(self):
        return self._client

    def process_content(self):
        pass

    def editorial(self):
        l = self.editorial_list()
        if l:
            return List(
                *[ContainerElement(name, html_type='a', classes={'editorial-link'}, additionals={'href': link}) for
                  name, link in l],
                classes={'editorial-list'}
            )
        return ''

    def editorial_list(self):
        return []

    def has_url_query(self):
        return bool(self._url.get_query)

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

    @property
    def compiled(self):
        if self.check_own_permission():
            self._process_queries()
            return super().compiled
        else:
            return Model('page', content=str(html_message.error_message(401)))