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


def parse_url(url):
    (path, location, query) = split_path(path=url)

    def notempty(a):
        return a is not None and a is not ''

    path = [word for word in filter(notempty, path.split('/'))]
    query = [argument for argument in filter(notempty, query.split('?'))]
    query = {argument: value for (argument, value) in [pair.split('=') for pair in query]}
    return path, location, query