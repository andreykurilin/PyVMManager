    #!/usr/bin/env python

from ConfigParser import ConfigParser
import os

__author__ = 'akurilin'
_possible_files = [
    "~/.config/pyvm.conf",
    "/etc/pyvm/settings.ini",
    "/etc/pyvm.conf"]


def get_config_file():
        for possible_file in _possible_files:
            if os.path.isfile(possible_file):
                return possible_file


class Settings(object):
    def __init__(self, settings_file=get_config_file()):
        self.config = ConfigParser()
        self.config.read(settings_file)

    def _get_section_settings(self, section):
        if section not in self.config.sections():
            return None
        else:
            section_settings = {}
            options = self.config.options(section)
            for option in options:
                value = self.config.get(section, option)
                if value[0] == '(' and value.__len__() > 1:
                    value = value.replace("(", "").\
                        replace(")", "").\
                        replace("\'", "")
                    value = tuple(value.split(", "))
                if value == "None":
                    value = None
                section_settings[option] = value
            return section_settings

    def __getattr__(self, name):
        if name in self.config.sections():
            return self._get_section_settings(name)
        else:
            return self.config.sections()

conf = Settings()