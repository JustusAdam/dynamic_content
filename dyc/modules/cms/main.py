"""
Main file that runs the application.
"""
import os
from pathlib import Path
import sys

__author__ = 'justusadam'

_basedir = Path(__file__).parent.parent.parent.resolve()

# add framework to pythonpath
if not str(_basedir.parent) in sys.path:
    sys.path.append(str(_basedir.parent))

os.chdir(str(_basedir))


def main():
    from dyc.application import Config
    from dyc.util.config import read_config
    from dyc.modules.cms.app import MainApp

    config = read_config('modules/cms/config')
    MainApp(Config(server_arguments=config['server_arguments'])).start()


if __name__ == '__main__':
    main()