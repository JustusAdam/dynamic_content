from application.config import ModuleConfig
from . import tokens
from application.fragments import AppFragment

__author__ = 'justusadam'


class FormApp(AppFragment):
    def validation_hook(self, url):
        # TODO make the database connection be held by the object
        if 'form_token' in url.post:
            print(str(url.get_query))
            return tokens.validate(str(url), url.post['form_token'][0])
        return True

    def setup_fragment(self):
        from .database_operations import FormOperations
        fo = FormOperations()
        fo.init_tables()


class FormConfig(ModuleConfig):
    pass