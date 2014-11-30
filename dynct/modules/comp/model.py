from dynct.backend.orm import *
from dynct.core.model import Theme

__author__ = 'justusadam'


class Common(BaseModel):
    name = CharField(unique=True)
    region = CharField()
    weight = IntegerField(default=0)
    theme = ForeignKeyField(Theme)
    show_title = BooleanField()
    render_args = CharField()