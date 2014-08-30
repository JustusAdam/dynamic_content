from includes.basic_handlers import SimplePageHandler

__author__ ='justusadam'


class EntityPageHandler(SimplePageHandler):

    def __init__(self, page_id, get_query):
        super().__init__(page_id=page_id, get_query=get_query)
        self.content_type = self.get_content_type()

    def get_content(self):
        pass

    def get_title(self):
        pass

    def get_content_type(self):
        return self.db.select(from_table='entity', columns='content_type', query_tail='where id = ' + self.page_id)

    def get_used_fields(self):
        return sorted(self.db.select(from_table='page_fields', columns=('id', 'weight'),
                              query_tail='where content_type = ' + self.content_type), key=lambda a: a[1])



class EditEntityHandler(EntityPageHandler):
    pass