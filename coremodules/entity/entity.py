from includes.basic_handlers import SimplePageHandler

__author__ ='justusadam'


class EntityPageHandler(SimplePageHandler):

    def __init__(self, page_id, get_query):
        super().__init__(db, page_id)

    def get_content(self):
        pass

    def get_title(self):
        pass