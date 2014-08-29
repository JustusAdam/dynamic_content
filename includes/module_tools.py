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
    from .bootstrap import COREMODULES_DIRECTORY, MODULES_DIRECTORY
    from importlib import import_module

    for module_directory in (MODULES_DIRECTORY, COREMODULES_DIRECTORY):
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