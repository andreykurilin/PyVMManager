#!/usr/bin/env python
import os
from server.utils.settings import Settings

__author__ = 'akurilin'

conf = Settings(os.path.join(os.path.dirname(__file__), "settings.ini"))