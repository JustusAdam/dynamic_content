import pathlib
import inspect
import collections
from dyc.backend import orm

from . import Component
from dyc.modules import Module
from dyc.util import config, lazy, console, module as _module
from dyc.includes import settings
from dyc.includes import log


__author__ = 'Justus Adam'
__version__ = '0.3'


basedir = str(pathlib.Path(__file__).parent.parent.resolve())

json_config_name = 'config.json'

python_config_name = 'module_config'


def get_module_conf(path:str, module):
    dir_ = pathlib.Path(path)
    if dir_.is_dir() and json_config_name in dir_.iterdir():
        return config.read_config(str(dir_ / json_config_name))
    else:
        if hasattr(module, python_config_name):
            return getattr(module, python_config_name)
    raise NotImplemented(path)


def activate_module(module_name):
    # console.cprint('Activating module: ' + module_name)
    if is_active(module_name):
        console.print_error('Module ' + module_name + ' is already active.')
        return True
    path = get_module_path(module_name)
    m = _module.import_by_path('dyc/' + path)
    if path is None:
        console.print_error('Module ' + module_name + ' could not be activated')
        return False
    module_conf = get_module_conf('dyc/' + path, m)
    module_conf['path'] = path
    init_tables(m)
    return _set_module_active(module_conf['name'])


def init_tables(m):
    for item in dir(m):
        item = getattr(m, item)
        if inspect.isclass(item) and issubclass(item, orm.BaseModel):
            try:
                item.create_table()
            except Exception as e:
                print(e)
                log.write_error('create_table:', e)


def get_module_id(module_name):
    return Module.get(machine_name=module_name).id


def get_module_path(module):
    return Module.get(machine_name=module).module_path


def _set_module_active(module_name):
    a = Module.get(machine_name=module_name)
    a.enabled = True
    a.save()


def is_active(module_name):
    result = Module.get(module_name=module_name)
    if result:
        return result.enabled
    else:
        return False


def register_installed_modules():
    register_modules(discover_modules())


def discover_modules():
    for directory in (
        settings.MODULES_DIRECTORIES +
        settings.COREMODULES_DIRECTORIES
        ):
        path = pathlib.Path(directory)
        if not path.exists():
            u = input(
                'The module directory {} does not exist yet, '
                'would you like me to create it? [Y|n]'.format(path)
                )
            if u.lower() in ('n', 'no'):
                continue
            if not path.parent.exists():
                path.parent.mkdir()
            path.mkdir()
        for file in filter(
                lambda s: ((s.is_dir()
                            or s.suffix == '.py')
                           and not s.name.startswith('_')),
                path.iterdir()):
            yield {
                'name': str(file.stem),
                'path': str(file)
                }


def register_modules(r_modules):
    if isinstance(r_modules, dict):
        register_single_module(r_modules)
    elif hasattr(r_modules, '__iter__'):
        for module in r_modules:
            register_single_module(module)
    else:
        raise ValueError


def register_single_module(moduleconf):
    assert isinstance(moduleconf, dict)
    # console.cprint('registering module ' + moduleconf['name'])
    try:
        module = Module.get(machine_name=moduleconf['name'])
        if module.path != moduleconf['path']:
            module.path = moduleconf['path']
            module.save()
    except orm.DoesNotExist:
        Module.create(machine_name=moduleconf['name'], path=moduleconf['path'])


def get_active_modules():
    modules = Module.select().where(Module.enabled == True)
    modules = tuple(modules)
    return {
        item.machine_name: _module.import_by_path('dyc/' + item.path)
        for item in modules
        }


@Component("Modules")
class Modules(dict, lazy.Loadable):
    """
    Immutable Module dictionary.
    """

    def __init__(self):
        super().__init__()

    def reload(self):
        self.load()

    def load(self):
        register_installed_modules()
        all_ = get_active_modules()
        for name, value in all_.items():
            dict.__setitem__(self, name, value)
        self.loaded = True

    @lazy.ensure_loaded
    def __getitem__(self, key):
        if isinstance(key, Module):
            key = key.machine_name
        return super().__getitem__(key)

    def __setitem__(self, key, value):
        raise PermissionError

    @lazy.ensure_loaded
    def _get_handlers(self, func, single_value):
        if single_value:
            acc = {}
        else:
            acc = collections.defaultdict(list)

        for a in self:
            for b in filter(
                lambda s: not s.startswith('_'),
                self[a].__dict__.keys()
                ):
                if func(b, getattr(self[a], b)):
                    if single_value:
                        acc[a] = getattr(self[a], b)
                    else:
                        acc[a].append(getattr(self[a], b))

        return acc

    @lazy.ensure_loaded
    def get_handlers_by_class(self, class_, single_value=False):
        return self._get_handlers(
            lambda a, b: inspect.isclass(b) and issubclass(b, class_), single_value
            )

    @lazy.ensure_loaded
    def get_handlers_by_name(self, name:str, single_value=False):
        if name.startswith('_'):
            raise TypeError(
                'name',
                'identifier on non-hidden attribute (does not start with \'_\')'
                )
        return self._get_handlers(
            lambda a, b: b == name, single_value
            )

    @lazy.ensure_loaded
    def __str__(self):
        return super().__str__()
