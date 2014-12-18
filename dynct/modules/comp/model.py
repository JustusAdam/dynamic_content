from dynct.backend import orm
from dynct.core import model as coremodel

__author__ = 'justusadam'


class Common(orm.BaseModel):
    machine_name = orm.CharField()
    region = orm.CharField()
    weight = orm.IntegerField(default=0)
    theme = orm.ForeignKeyField(coremodel.Theme)
    show_title = orm.BooleanField()
    render_args = orm.CharField(null=True)