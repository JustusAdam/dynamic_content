"""some of the frameworks own miscellaneous scanner hooks"""
from . import includes
from .machinery import scanner, component, linker


__author__ = 'Justus Adam'
__version__ = '0.1'


class NonOverwritingSettingsLink(linker.Link):
    __slots__ = 'variable',

    def __init__(self, variable):
        assert isinstance(variable, dict)
        super().__init__()
        self.variable = variable

    def unlink_action(self):
        pass

    @component.inject_method(includes.SettingsDict)
    def link_action(self, settings:dict):
        for k, v in self.variable.items():
            settings.setdefault(k, v)


class OverwritingSettingsLink(NonOverwritingSettingsLink):
    """link custom default settings keys"""

    __slots__ = 'deleted',

    def __init__(self, variable):
        super().__init__(variable)
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



@scanner.SingleNameHook.make('added_default_settings')
def handle_settings_keys(variable):
    return NonOverwritingSettingsLink(variable)


@scanner.SingleNameHook.make('overwrite_settings_keys')
def handle_settings_keys_overwrite(variable):
    return OverwritingSettingsLink(variable)