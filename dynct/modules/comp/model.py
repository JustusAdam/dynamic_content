from dynct.backend.orm import *
from dynct.core import model as coremodel

__author__ = 'justusadam'


class Common(BaseModel):
    machine_name = CharField()
    region = CharField()
    weight = IntegerField(default=0)
    theme = ForeignKeyField(coremodel.Theme)
    show_title = BooleanField()
    render_args = CharField(null=True)