from dynct.backend import orm

__author__ = 'justusadam'


class ARToken(orm.BaseModel):
    form_id = orm.CharField()
    token = orm.BlobField()