import os

__author__ = 'justusadam'


class requiredir:

    def __init__(self, directory):
        self.directory = directory
        self.curr_dir = os.getcwd()

    def __call__(self, f):
        self.curr_dir = os.getcwd()

        def wrapper(*args, **kwargs):
            os.chdir(self.directory)
            f(*args, **kwargs)
            os.chdir(self.curr_dir)

        return wrapper