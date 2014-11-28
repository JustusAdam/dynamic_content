"""
Main file that runs the application.
"""
import os
from pathlib import Path
import sys

__author__ = 'justusadam'

_basedir = Path(__file__).parent.resolve()

# if framework is not in the path yet, add it and import it
if not str(_basedir.parent) in sys.path:
    sys.path.append(str(_basedir.parent))

os.chdir(str(_basedir))

del _basedir

def main():
    from dynct.application import Config, Application
    from dynct.util.config import read_config

    config = read_config('modules/cms/config')
    Application(Config(server_arguments=config['server_arguments'])).start()


if __name__ == '__main__':
    main()