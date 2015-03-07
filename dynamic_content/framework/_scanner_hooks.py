"""some of the frameworks own miscellaneous scanner hooks"""
from . import includes
from .machinery import scanner, component, linker


__author__ = 'Justus Adam'
__version__ = '0.1'


class SettingsLink(linker.Link):
    """link custom default settings keys"""

    __slots__ = 'variable', 'deleted'

    def __init__(self, variable):
        assert isinstance(variable, dict)
        super().__init__()
        self.variable = variable
        self.deleted = None

    @component.inject_method(includes.SettingsDict)
    def unlink_action(self, settings):
        """
        add potentially removed settings back to settings

        :param settings: injected settings
        :return: None
        """
        settings.update(self.deleted)

    @component.inject_method(includes.SettingsDict)
    def link_action(self, settings):
        """
        remove (and save) settings that would be overwritten
        by merging the custom settings and then merge the
        custom settings into the global settings dict

        :param settings: injected settings
        :return: None
        """
        self.deleted = {a: settings[a] for a in self.variable}
        settings.update(self.variable)


@scanner.SingleNameHook.make('settings_keys')
def handle_settings_keys(variable):
    return SettingsLink(variable)