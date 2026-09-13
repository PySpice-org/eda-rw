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

from edarw.objectifier import Objectifier, SchemaNode
from edarw.log import setup_logging

####################################################################################################

logger = setup_logging()

console = Console()

####################################################################################################

path = Path('../../librepcb-examples/calidou')
objectifier = Objectifier(path / 'circuit/circuit.lp')
# objectifier.dump()
objectifier.get_schema()
for key, value in SchemaNode.NODES.items():
    print(f"[blue]{key}[/]: {value}")
