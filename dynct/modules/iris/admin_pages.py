from dynct.core.mvc import content_compiler

__author__ = 'justusadam'


class Overview(content_compiler.Content):
    permission = 'access iris content overview'

    def process_content(self):
        pass

    def page_types(self):
        return ['iris']