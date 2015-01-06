from dyc.includes import settings

__author__ = 'Justus Adam'


def _active_cprint(*stuff, sep='', end='\n', file=None, flush=False):
    print(*stuff, sep=sep, end=end, file=file, flush=flush)


def _inactive_cprint(*stuff, sep='', end='\n', file=None, flush=False):
    pass


cprint = _active_cprint if settings.RUNLEVEL in [settings.RunLevel.debug, settings.RunLevel.testing] else _inactive_cprint