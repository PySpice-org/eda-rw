####################################################################################################
#
# EDA-RW — Python library to read/write EDA Sexpr file format
# Copyright (C) 2021 Fabrice SALVAIRE
# SPDX-License-Identifier: AGPL-3.0-or-later
#
####################################################################################################

__all__ = ['find']

####################################################################################################

from collections.abc import Iterable
from pathlib import Path

####################################################################################################

def find(file_name: str, directories: Iterable[str | Path]) -> Path:
    for directory in directories:
        for directory_path, _, file_names in Path(directory).walk():
            if file_name in file_names:
                return directory_path.joinpath(file_name)
    raise NameError(f"File {file_name} not found in directories {directories}")
