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

from edarw.eda.librepcb import Project
from edarw.log import setup_logging

####################################################################################################

logger = setup_logging()

console = Console()

####################################################################################################

path = Path('../../librepcb-examples/calidou')
project = Project.load(path)
circuit = project.circuit

indent = ' ' * 4

print()
console.rule()
for component in project.components:
    print(component)
    for signal in component.signal:
        print(indent, signal)
for symbol in project.symbols:
    print(symbol)
    print(symbol.to_json())

print()
console.rule()
for net in circuit.net:
    print(net)
    for signal in net.signals:
        print(indent, f"{signal.component.name}.{signal.signal_def.name}")
print()
for component in circuit.component:
    print(component)
    for attribute in component.attribute:
        print(indent, attribute)
    for signal in component.signal:
        print(indent, signal)
        print(indent * 2, signal.signal_def)

schematic = project.schematic
print(schematic.to_json())
