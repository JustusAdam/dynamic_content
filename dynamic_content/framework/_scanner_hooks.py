"""some of the frameworks own miscellaneous scanner hooks"""
from . import includes
from .machinery import scanner, component, linker, registry


__author__ = 'Justus Adam'
__version__ = '0.1'


@scanner.NameHook.make('finalize')
class UnloadingFunction(linker.SimpleLink):
    """unloading function to run every time the module gets unactivated"""
    __slots__ = ()

    def link_action(self):
        pass

    def unlink_action(self):
        self.variable()


@scanner.NameHook.make('init')
class LoadingFunction(linker.SimpleLink):
    """loader func to run every time the module gets activated"""
    __slots__ = ()

    def link_action(self):
        self.variable()

    def unlink_action(self):
        pass


@scanner.NameHook.make('install')
class InstallFunction(linker.SimpleLink):
    """
    Functions to run once when the module gets first activated
    """
    __slots__ = ()

    def link_action(self):
        if self.module not in registry.Registry()['modules']:
            self.variable()

    def unlink_action(self):
        pass


@scanner.NameHook.make('deinstall')
class DeinstallFunction(linker.SimpleLink):
    """Function to run if the module gets deinstalled"""
    __slots__ = ()

    def link_action(self):
        pass

    def unlink_action(self):
        pass


@scanner.NameHook.make('added_default_settings')
class NonOverwritingSettingsLink(linker.SimpleLink):
    """Link updating settings with added defaults"""
    __slots__ = ()

    def __init__(self, module, variable):
        assert isinstance(variable, dict)
        super().__init__(module, variable)

    def unlink_action(self):
        pass

    @component.inject_method(includes.SettingsDict)
    def link_action(self, settings:dict):
        for k, v in self.variable.items():
            settings.setdefault(k, v)


@scanner.NameHook.make('overwrite_settings_keys')
class OverwritingSettingsLink(NonOverwritingSettingsLink):
    """overwrite settings keys"""

    __slots__ = 'deleted',

    def __init__(self, module, variable):
        super().__init__(module, variable)
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