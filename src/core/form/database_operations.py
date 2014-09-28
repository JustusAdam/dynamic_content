from core.database_operations import Operations, escape

__author__ = 'justusadam'


class FormOperations(Operations):

  _tables = {'form_tokens', 'form_handlers'}

  _queries = {
    'mysql': {
      'get_handler': 'select handler_module from form_handlers where path_prefix={prefix};',
      'add_handler': 'insert into form_handlers (path_prefix, handler_module) values ({prefix}, {handler_mule});'
    }
  }

  def get_handler(self, prefix):
    self.execute('get_handler', prefix=escape(prefix))
    return self.cursor.fetchone()[0]

  def add_handler(self, prefix, handler_module):
    self.execute('add_handler', prefix=escape(prefix), handler_module=escape(handler_module))