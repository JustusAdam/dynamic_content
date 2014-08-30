__author__ = 'justusadam'


def get_page_handlers(db):
    return {
        'admin': {
            'type': 'admin',
            'module': 'coremodules/adminpages'
        },
        'entity': {
            'type': 'entity',
            'module': 'coremodules/entity'
        },
        'setup': {
            'type': 'setup',
            'module': 'includes/setup'
        }
    }


def get_modules():
    modules = {}
    import os
    from tools.config_tools import read_config
    from importlib import import_module

    bootstrap = read_config('includes/bootstrap')

    for module_directory in (bootstrap['MODULES_DIRECTORY'], bootstrap['COREMODULES_DIRECTORY']):
        for file in os.listdir(module_directory):
            try:
                if file.endswith('.py'):
                    file = file[:-3]
                file = module_directory + '.' + file
                modules[import_module(file).name] = file
            except (ImportError, AttributeError) as err:
                print(err)
                pass
    return modules