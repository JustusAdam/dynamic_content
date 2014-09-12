__author__ = 'justusadam'


def singleton(class_):
    """
    This implements a function that is to be used as a decorator for a class in order to make it a singleton.

    Credit for this code goes to 'theheadofabroom' on stackoverflow.com

    http://stackoverflow.com/questions/6760685/creating-a-singleton-in-python

    :param class_:
    :return:
    """
    instances = {}
    def get_instance(*args, **kwargs):
        if class_ not in instances:
            instances[class_] = class_(*args, **kwargs)
        return instances[class_]
    return get_instance