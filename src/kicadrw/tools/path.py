####################################################################################################
#
# KiCad-RW — Python library to read/write KiCad Sexpr file format
# Copyright (C) 2021 Fabrice SALVAIRE
# SPDX-License-Identifier: AGPL-3.0-or-later
#
####################################################################################################

__all__ = ['find']

####################################################################################################

from pathlib import Path
import os

####################################################################################################

def find(file_name: str, directories: list[str]) -> Path:
    for directory in directories:
        for directory_path, sub_directories, file_names in os.walk(directory):
            if file_name in file_names:
                return Path(directory_path, file_name)
    raise NameError(f"File {file_name} not found in directories {directories}")
