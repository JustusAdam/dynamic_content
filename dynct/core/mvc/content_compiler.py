from http import cookies
from dynct.core.mvc import model as _model
from dynct.errors import html_message
from dynct.modules.comp import html


__author__ = 'justusadam'


class ContentCompiler(object):
    pass


class ModelBasedContentCompiler(ContentCompiler):
    _view_name = 'page'

    def __call__(self, model, *args, **kwargs):
        return self._view_name


class Content(ModelBasedContentCompiler):
    def process_content(self):
        pass




    def __call__(self, model, *args, **kwargs):
        page = self.get_page()




    def compile(self):
        if self.check_own_permission():
            model = super().compile()
            if self.cookies:
                model.cookies = self.cookies
            c = model
        else:
            c = _model.Model('page', content=str(html_message.error_message(401)))
        return c