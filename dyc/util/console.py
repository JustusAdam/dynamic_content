from dyc.includes import settings


__author__ = 'Justus Adam'
__version__ = '0.2'


cprint = print if settings.RUNLEVEL in [settings.RunLevel.debug, settings.RunLevel.testing] else lambda *args, **kwargs: None
