from ..database_operations import Operations, escape

__author__ = 'justusadam'


class AdminOperations(Operations):
  _queries = {
    'mysql': {
      'get_all_categories': 'select machine_name, display_name from admin_categories;',
      'get_subcategories': 'select machine_name, display_name, category from admin_sections {cond} order by subcategory, weight;'
    }
  }

  def get_categories(self):

    self.execute('get_all_categories')
    return self.cursor.fetchall()

  def get_subcategories(self, *categories):
    cond = ''
    if categories:
      acc = []
      for item in categories:
        acc.append('category=' + escape(item))
      cond = 'where ' + ' and '.join(acc)
    self.execute('get_subcategories', cond=cond)
    return self.cursor.fetchall()
