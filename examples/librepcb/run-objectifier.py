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
from edarw.text_buffer import TextBuffer

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

project_path = Path('../../librepcb-examples')
# file_path = 'calidou/circuit/circuit.lp'
# file_path = 'calidou/schematics/main/schematic.lp'
file_path = 'can2usb/boards/default/board.lp'
path = project_path / file_path
objectifier = Objectifier(path)

# objectifier.dump()

objectifier.get_schema()
# for path, node in SchemaNode.NODES.items():
#     print(f"[blue]{path}[/]: {node}")

buffer = TextBuffer()

def make_class_name(node: SchemaNode) -> str:
    return node.name.title().replace('_', '')

def make_field_type(parent: SchemaNode, node: SchemaNode, is_list: bool) -> tuple[str, str]:
    if len(node):
        class_name = make_class_name(node)
        if is_list:
            return f'list[{class_name}]', ''
        else:
            return class_name, ''
    else:
        type_patterns = list(node.child_types)
        if len(type_patterns) > 1:
            # raise NameError('More than one type pattern for {node}')
            return '...', '{type_patterns}'
        types = type_patterns[0]
        match len(types):
            case 0:
                # raise NameError('Empty type for {node}')
                return '...', f'Empty type ! {type_patterns}'
            case 1:
                field_type = types[0]
                if 'Symbol' in field_type:
                    childs = [_.get_child(node.name) for _ in parent._instances]
                    values = list(set(str(_.childs[0]) for _ in childs if _ is not None))
                    if 'true' in values or 'false' in values:
                        return 'bool', ''
                    if values[0].count('-') == 4:
                        return 'UUID', ''
                    return 'str', str(values)
                return field_type, ''
            case _:
                return f'tuple[{', '.join(types)}]', ''

def make_class(node: SchemaNode) -> None:
    global buffer
    buffer.new_line()
    buffer += '#'*100
    buffer.new_line()
    class_name = make_class_name(node)
    buffer += f"class {class_name}(SexpWrapper):"
    buffer.indent()
    buffer += f"CAR = '{node.name}'"

    child_map: dict[str, SchemaNode] = {child.name: child for child in node}

    child_patterns = list(set(simplify_child_types(_) for _ in node.child_types))
    # if not child_patterns or max(len(_) for _ in child_patterns) == 1:
    #     continue
    common = find_common_part(child_patterns)
    for field in common:
        try:
            is_list = field.endswith('*')
            if is_list:
                field = field[:-1]
            child = child_map[field]
            field_type, comment = make_field_type(node, child, is_list)
            if comment:
                comment = f'  # {comment}'
            buffer += f"{field}: {field_type}{comment}"
        except KeyError:
            buffer += f"# {field}:"
    patterns = sorted(child_patterns, reverse=True, key=len)
    for _ in patterns:
        tail = _[len(common):]
        if tail:
            buffer += '# ' + str(tail)
    for field in patterns[0][len(common):]:
        if field.endswith('*'):
            field = field[:-1]
        child = child_map[field]
        field_type, _ = make_field_type(node, child, True)
        buffer += f"{field}: {field_type}"

    buffer.dedent()

def on_leave(node: SchemaNode) -> None:
    if len(node) and node.name != '/':
        make_class(node)

SchemaNode.root().depth_first_search(on_leave=on_leave)  # ty: ignore[invalid-argument-type]
print(buffer)
