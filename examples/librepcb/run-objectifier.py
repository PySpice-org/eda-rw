####################################################################################################
#
# EDA-RW — Python library to read/write EDA Sexpr file format
# Copyright (C) 2021 Fabrice SALVAIRE
# SPDX-License-Identifier: AGPL-3.0-or-later
#
####################################################################################################

from pathlib import Path

from rich import print
from rich.console import Console

from edarw.log import setup_logging
from edarw.objectifier import Objectifier, PythonModuleGenerator

####################################################################################################

logger = setup_logging()

console = Console()

####################################################################################################

project_path = Path('../../librepcb-examples')
# file_path = 'calidou/circuit/circuit.lp'
# file_path = 'calidou/schematics/main/schematic.lp'
file_path = 'can2usb/boards/default/board.lp'
path = project_path / file_path
objectifier = Objectifier(path)
generator = PythonModuleGenerator(objectifier)
print(generator)
