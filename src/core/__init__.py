__author__ = 'justusadam'

from .module_operations import register_installed_modules
from .modules import Modules
from . import database_operations as dbo

name = 'olymp'

role = 'core'

# TODO refactor everything to get core module and move it here


def load_modules():
    m = Modules()
    m.reload()
    return m


class InitMod:

    operations = {}

    def init_ops(self):
        return {a: self.operations[a]() for a in self.operations}

    def execute(self, drop_tables=True, fill_tables=True):
        ops = self.init_ops()
        for op in ops:
            op.init_tables(drop_tables)
        if fill_tables:
            self.fill_tables(ops)

    def fill_tables(self, ops):
        pass


class InitCore(InitMod):
    operations = {
        'ch': dbo.ContentHandlers,
        'alias': dbo.Alias
    }

    def fill_tables(self, ops):
        ops['alias'].add_alias('/iris/1', '/welcome')


init_class = InitCore