from dycm.commons import model

__author__ = 'Justus Adam'
__version__ = '0.1'


def setUp():
    assert model.Menu._meta.database.database == ':memory:'