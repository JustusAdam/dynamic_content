from framework.backend import orm

__author__ = 'Justus Adam'


class Category(orm.BaseModel):
    machine_name = orm.CharField(unique=True)
    display_name = orm.CharField()
    description = orm.TextField(null=True)
    weight = orm.IntegerField(default=0)


class Subcategory(orm.BaseModel):
    display_name = orm.CharField()
    description = orm.TextField(null=True)
    weight = orm.IntegerField(default=0)
    category = orm.ForeignKeyField(Category)
    machine_name = orm.CharField(unique=False)


class AdminPage(orm.BaseModel):
    machine_name = orm.CharField(unique=False)
    display_name = orm.CharField()
    description = orm.TextField(null=True)
    weight = orm.IntegerField(default=0)
    subcategory = orm.ForeignKeyField(Subcategory)