####################################################################################################
#
# EDA-RW — Python library to read/write EDA Sexpr file format
# Copyright (C) 2021 Fabrice SALVAIRE
# SPDX-License-Identifier: AGPL-3.0-or-later
#
####################################################################################################

from collections.abc import Iterable, Iterator
from pathlib import Path

from rich import print
from rich.console import Console

from edarw.objectifier import Objectifier, SchemaNode, StringList
from edarw.log import setup_logging

####################################################################################################

logger = setup_logging()

console = Console()

####################################################################################################

def simplify_child_types(child_types: StringList) -> StringList:
    new_list: list[str] = []
    prev = None
    while True:
        if prev is None:
            prev = child_types.pop()
            new_list.append(prev)
        else:
            _ = child_types.pop()
            if _ != prev:
                new_list.append(_)
                prev = _
            elif not new_list[-1].endswith('*'):
                new_list[-1] += '*'
        if not child_types:
            break
    return StringList(new_list)

def find_common_part(child_patterns: list[list[str]]) -> list[str]:
    match len(child_patterns):
        case 0:
            return []
        case 1:
            return child_patterns[0]
        case _:
            common = []
            for i in range(min(len(_) for _ in child_patterns)):
                items = list(set([_[i] for _ in child_patterns]))
                if len(items) == 1:
                    common.append(items[0])
                else:
                    break
            return common

####################################################################################################

projec_path = Path('../../librepcb-examples/calidou')
# path = projec_path / 'circuit/circuit.lp'
path = projec_path / 'schematics/main/schematic.lp'
objectifier = Objectifier(path)

# objectifier.dump()

objectifier.get_schema()
# for path, node in SchemaNode.NODES.items():
#     print(f"[blue]{path}[/]: {node}")

for path, node in SchemaNode.NODES.items():
    # print('ct', node.child_types)
    child_patterns = list(set(simplify_child_types(_) for _ in node.child_types))
    # print('cp', child_patterns)
    if not child_patterns or max(len(_) for _ in child_patterns) == 1:
        continue
    common = find_common_part(child_patterns)
    print()
    console.rule()
    print(path)
    print(common)
    print()
    for _ in sorted(child_patterns, reverse=True, key=len):
        tail = _[len(common):]
        if tail:
            print(tail)
