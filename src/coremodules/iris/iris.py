from ..olymp.basic_page_handlers import BasicPageHandler

__author__ = 'justusadam'


class IrisContentHandler:

    def __init__(self, url):
        super().__init__(url)
        self.content_type = self.get_content_type()
        self.page_type = 'iris'

    def get_content(self):
        pass

    def get_title(self):
        pass


class EditIrisHandler(IrisContentHandler):
    pass


class IrisBaseFieldHandler():
    pass


class IrisBaseFieldEditHandler(IrisBaseFieldHandler):
    pass