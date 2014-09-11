from urllib import parse
__author__ = 'justusadam'


def split_path(path):
    if path.find('?') == -1:
        query = ''
    else:
        (path, query) = path.split('?', 1)
    if path.find('#') == -1:
        location = ''
    else:
        (path, location) = path.split('#', 1)
    return path, location, query


def join_path(path, location, query):
    if location != '':
        location = '#' + location
    if query != '':
        query = '?' + query
    return path + location + query


class Url:
    def __init__(self, url, post_query=None):
        (path, location, query) = split_path(url)
        self._path = UrlPath(path)
        self._location = UrlLocation(location)
        self._get_query = UrlQuery(query)
        self.post_query = post_query

        self.page_id = None
        self.page_type = None
        self.page_modifier = None
        self.parse_path()

    def parse_path(self):
        if len(self.path) > 0:
            self.page_type = self.path[0]
            self.page_id = 0
        if len(self.path) > 1:
            if self.path[1].isdigit():
                self.page_id = int(self.path[1])
            elif self.path[1].isalpha():
                self.page_modifier = self.path[1]
        if len(self.path) > 2 and not self.page_modifier:
            self.page_modifier = self.path[2]

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

    @property
    def post_query(self):
        return self._post_query

    @post_query.setter
    def post_query(self, value):
        if isinstance(value, UrlQuery):
            self._post_query = value
        else:
            self._post_query = UrlQuery(value)

    def __str__(self):
        return str(self._path) + str(self._location) + str(self._get_query)

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
        self._path = list(filter(lambda s: s is not '' and s is not None, value.split('/')))

    def __str__(self):
        acc = ''
        if self.starting_slash:
            acc += '/'
        acc += '/'.join(self.path)
        if self.trailing_slash:
            acc += '/'
        return acc

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
        self._location = value

    def __str__(self):
        if self._location:
            return '#' + self.location
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
            return '?' + '&'.join(tuple(parse.quote_plus(a) + '=' + self.query[a] for a in self.query.keys()))
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