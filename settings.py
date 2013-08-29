#!/usr/bin/env python

import ConfigParser

__author__ = 'akurilin'


class Settings(object):
    def __init__(self):
        self.config = ConfigParser.ConfigParser()
        self.config.read("settings.ini")

    def get_section_settings(self, section):
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
            return self.get_section_settings(name)
        else:
            return self.config.sections()

conf = Settings()
