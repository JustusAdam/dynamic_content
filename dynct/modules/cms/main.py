"""
Main file that runs the application.
"""
import os
from pathlib import Path
import sys


_basedir = Path(__file__).parent.parent.parent.resolve()

# add framework to pythonpath
if not str(_basedir.parent) in sys.path:
    sys.path.append(str(_basedir.parent))

os.chdir(str(_basedir))

from dynct.application import Config
from dynct.util.config import read_config
from dynct.modules.cms.app import MainApp

config = read_config('modules/cms/config')

__author__ = 'justusadam'


def main():
    MainApp(Config(server_arguments=config['server_arguments'])).run()


if __name__ == '__main__':
    main()