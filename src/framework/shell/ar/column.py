__author__ = 'justusadam'


class Column:

  _null_allowed = True

  def __init__(self, name, data_type, null_allowed, key, default, extra):
    self.name = name
    self.data_type = data_type
    self.null_allowed = null_allowed
    self.key = key
    self.default = default
    self.extra = extra


  @property
  def null_allowed(self):
    return self._null_allowed

  @null_allowed.setter
  def null_allowed(self, val):
    if isinstance(val, bool):
      self._null_allowed = val
    elif isinstance(val, str):
      if val.lower() == 'yes':
        self._null_allowed = True
      elif val.lower() == 'no':
        self._null_allowed = False
      else:
        raise ValueError
    else:
      raise ValueError

  def __str__(self):
    return ' '.join([self.name, self.data_type, str(self.null_allowed), self.key, str(self.default), self.extra])