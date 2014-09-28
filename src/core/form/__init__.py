from .database_operations import FormOperations

__author__ = 'justusadam'


def handle_post(url, post_query):
  pass


def register_form(path_prefix, handler_module):
  FormOperations().add_handler(path_prefix, handler_module)

def prepare():
  fo = FormOperations()
  fo.init_tables()