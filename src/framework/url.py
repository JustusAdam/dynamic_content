"""
Implementation of custom, object oriented tools for url parsing.

In part uses the standard library to parse and escape/unescape queries. Implementation might be subject to change in
the future, incorporate more of the standard library.
"""

from urllib import parse

__author__ = 'justusadam'


class Url:

  post = None

  def __init__(self, url, post=None):
    parsed = parse.urlsplit(url)
    self._path = UrlPath(parsed.path)
    self._location = UrlLocation(parsed.fragment)
    self._get_query = UrlQuery(parsed.query)
    if post:
      if isinstance(post, UrlQuery):
        self.post = post
      else:
        self.post = UrlQuery(post)

    self.page_id = 1
    self.page_type = None
    self.page_modifier = 'show'
    self.parse_path()

  def parse_path(self):
    self.tail = []
    if len(self.path) > 0:
      self.page_type = self.path[0]
      self.page_id = 0
    if len(self.path) > 1:
      if self.path[1].isdigit():
        self.page_id = int(self.path[1])
        self.tail = self.path[2:]
      elif self.path[1].isalpha():
        self.tail = self.path[1:]
    if len(self.path) > 2:
      if self.tail:
        self.page_modifier = self.tail[0]

  @property
  def path(self):
    return self._path

  @path.setter
  def path(self, value):
    if isinstance(value, UrlPath):
      self._path = value
    else:
      self._path = UrlPath(value)
      self.parse_path()

  @property
  def location(self):
    return self._location

  @location.setter
  def location(self, value):
    if isinstance(value, UrlLocation):
      self._location = value
    else:
      self._location = UrlLocation(value)

  @property
  def get_query(self):
    return self._get_query

  @get_query.setter
  def get_query(self, value):
    if isinstance(value, UrlQuery):
      self._get_query = value
    else:
      self._get_query = UrlQuery(value)

  def __str__(self):
    return parse.urlunsplit(('', '', str(self._path), str(self._get_query), str(self._location)))

  def __bool__(self):
    return bool(self._path)


class UrlPath:
  def __init__(self, path):
    self.path = path

  @property
  def path(self):
    return self._path

  @path.setter
  def path(self, value):
    self.trailing_slash = value.endswith('/') and len(value) > 1
    self.starting_slash = value.startswith('/')
    self._path = list(filter(lambda s: s is not '' and s is not None, parse.unquote_plus(value).split('/')))

  def __str__(self):
    return self.prt_to_str()

  def prt_to_str(self, start=0, stop=0):
    if stop == 0:
      slc = self._path[start:]
    else:
      slc = self._path[start:stop]
    acc = ''
    if self.starting_slash:
      acc += '/'
    acc += '/'.join(slc)
    if self.trailing_slash:
      acc += '/'
    return parse.quote(acc)


  def __getitem__(self, item):
    return self.path[item]

  def __setitem__(self, key, value):
    self._path[key] = value

  def __len__(self):
    return len(self.path)

  def __contains__(self, item):
    return item in self.path

  def __bool__(self):
    return bool(self.path)


class UrlLocation:
  def __init__(self, location):
    self.location = location

  @property
  def location(self):
    return self._location

  @location.setter
  def location(self, value):
    if value.startswith('#'):
      value = value[1:]
    self._location = parse.unquote(value)

  def __str__(self):
    if self._location:
      return '#' + parse.quote(self.location)
    else:
      return ''

  def __bool__(self):
    return bool(self.location)


class UrlQuery:
  def __init__(self, query):
    self.query = query

  @property
  def query(self):
    return self._query

  @query.setter
  def query(self, value):
    if not value:
      self._query = {}
    elif isinstance(value, dict):
      self._query = value
    elif isinstance(value, str):
      self._query = parse.parse_qs(value)

  def __str__(self):
    if self._query:
      return parse.urlencode(self._query, doseq=True)
    else:
      return ''

  def __getitem__(self, item):
    return self.query[item]

  def __setitem__(self, key, value):
    self._query[key] = parse.quote_plus(value)

  def __contains__(self, item):
    if self.query:
      return item in self.query
    else:
      return False

  def __bool__(self):
    return bool(self.query)

  def keys(self):
    return self._query.keys()