"""
Main file that runs the application.
"""
from dynct.application import Config
from dynct.util.config import read_config
from dynct.modules.cms.app import MainApp

config = read_config('modules/cms/config')

__author__ = 'justusadam'


def main():
    MainApp(Config(server_arguments=config['server_arguments'])).run()


if __name__ == '__main__':
    main()
