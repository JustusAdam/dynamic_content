import importlib
from dyc.backend import orm
from dyc.util import decorators

__author__ = 'Justus Adam'


def import_modules(*modules):
    return tuple(import_single_module(module) for module in modules)


@decorators.multicache
def import_single_module(name, package=None):
    try:
        module_info = get_module(name) if package is None else get_module(package)
        if not module_info.enabled:
            raise PermissionError('Module {} is not enabled'.format(name))
        if package is None:
            return importlib.import_module(to_python_module_path('dyc/' + module_info.path))
        else:
            import_module(package)
            return importlib.import_module(to_python_module_path(name), to_python_module_path('dyc/' + module_info.path))
    except orm.DoesNotExist:
        raise AttributeError('Module {} does not exist\n{}'.format(name, tuple(str(a.machine_name) for a in Module.select())))


import_module = import_single_module


def to_python_module_path(path):
    python_conform_path = path.replace('/', '.')
    if python_conform_path.endswith('.py'):
        python_conform_path = python_conform_path[:-3]
    return python_conform_path


def get_module(name):
    return Module.get(machine_name=name)


class Module(orm.BaseModel):
    machine_name = orm.CharField(unique=True)
    path = orm.TextField()
    enabled = orm.BooleanField(default=False)