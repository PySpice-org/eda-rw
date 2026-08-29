####################################################################################################
#
# KiCad-RW — Python library to read/write KiCad Sexpr file format
# Copyright (C) 2021 Fabrice SALVAIRE
# SPDX-License-Identifier: AGPL-3.0-or-later
#
####################################################################################################

from pathlib import Path

import sys

####################################################################################################

import KiCadRW.tools.path as PathTools

####################################################################################################

class OsFactory:

    ##############################################

    def __init__(self) -> None:
        if sys.platform.startswith('linux'):
            self._name = 'linux'
        elif sys.platform.startswith('win'):
            self._name = 'windows'
        elif sys.platform.startswith('darwin'):
            self._name = 'osx'

    ##############################################

    @property
    def name(self) -> str:
        return self._name

    @property
    def on_linux(self) -> bool:
        return self._name == 'linux'

    @property
    def on_windows(self) -> bool:
        return self._name == 'windows'

    @property
    def on_osx(self) -> bool:
        return self._name == 'osx'

OS = OsFactory()

####################################################################################################

_this_file = Path(__file__).absolute()

class Path:

    kicadrw_module_directory = _this_file.parents[1]
    config_directory = _this_file.parent

####################################################################################################

class Logging:

    default_config_file = 'logging.yml'
    directories = (Path.config_directory,)

    ##############################################

    @staticmethod
    def find(config_file) -> Path:
        return PathTools.find(config_file, Logging.directories)
