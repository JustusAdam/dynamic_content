from dynct.core.mvc.content_compiler import Content

__author__ = 'justusadam'


class Overview(Content):
    permission = 'access iris content overview'

    def process_content(self):
        pass

    def page_types(self):
        return ['iris']