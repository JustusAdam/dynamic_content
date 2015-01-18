from dyc.includes import settings


__author__ = 'Justus Adam'
__version__ = '0.2'


cprint = print if settings.RUNLEVEL in (settings.RunLevel.DEBUG, settings.RunLevel.TESTING) else lambda *args, **kwargs: None
