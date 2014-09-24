from .database_operations import SessionOperations

__author__ = 'justusadam'


# This might not work
_so = None


@property
def so():
    global _so
    if not _so:
        _so = SessionOperations()
    return _so
