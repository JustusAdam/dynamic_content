from datetime import datetime

from dynct.backend.ar.base import ARObject


__author__ = 'justusadam'


def page(name):
    class Page(ARObject):
        _table = name

        def __init__(self, content_type, page_title, creator, published, date_created=datetime.utcnow()):
            super().__init__()
            self.content_type = content_type
            self.page_title = page_title
            self.creator = creator
            self.published = published
            self.date_created = date_created

        def get_id(self):
            return self._get_one_special_value('id', 'order by id desc limit 1')
    return Page