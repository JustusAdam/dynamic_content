from urllib.error import HTTPError
from core import Modules
from .database_operations import FormOperations

__author__ = 'justusadam'


def handle_post(url, post_query):
  handler_name = FormOperations().get_handler(url.page_type)
  if handler_name:
    handler = Modules()[handler_name](url, post_query)
    return handler.handle()
  else:
    raise HTTPError(str(url), 404, None, None, None)



def register_form(path_prefix, handler_module):
  FormOperations().add_handler(path_prefix, handler_module)

def prepare():
  fo = FormOperations()
  fo.init_tables()