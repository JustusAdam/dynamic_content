__author__ = 'justusadam'


class ComponentContainer(dict):
    def __init__(self):
        super().__init__()

    def __call__(self, *args, **kwargs):
        if len(args) == 0:
            raise AttributeError
        if len(args) == 1:
            if not kwargs:
                return self.__getitem__(args[0])
        return self.__getitem__(args[0])(*args[1:], **kwargs)


call_component = get_component = ComponentContainer()


del ComponentContainer


def _decorator(name):
    def inner(class_, *args, **kwargs):
        register(name, class_(*args, **kwargs))
        return class_
    return inner



Component = component = _decorator


def register(name, obj):
    get_component[name] = obj