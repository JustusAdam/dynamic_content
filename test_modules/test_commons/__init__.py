from dycm.commons import model

__author__ = 'Justus Adam'
__version__ = '0.1'


def setUp():
    for a in (
        model.Common,
        model.CommonData,
        model.CommonsConfig,
        model.Menu,
        model.MenuItem
    ):
        a.create_table()