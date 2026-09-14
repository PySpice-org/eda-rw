####################################################################################################
#
# EDA-RW — Python library to read/write EDA Sexpr file format
# Copyright (C) 2021 Fabrice SALVAIRE
# SPDX-License-Identifier: AGPL-3.0-or-later
#
####################################################################################################

__all__ = [
    'Objectifier',
]

####################################################################################################

import logging
import re
from collections.abc import Callable, Iterable, Iterator
from pathlib import Path
from typing import Any, Self, cast

import sexpdata as S
from rich import print
from sexpdata import Symbol

####################################################################################################

_module_logger = logging.getLogger(__name__)

# Fixme: it is recursive
type SexprType = list | int | float | str

####################################################################################################

def car_value(_: list) -> str:
    return S.car(_).value()

####################################################################################################

class StringList:
    """Convenient wrapper for an hashable list of strings"""

    PACK_SEPARATOR = '/'

    __slots__ = ['_strings']

    @classmethod
    def pack(cls, strings: Iterable[str]) -> str:
        return cls.PACK_SEPARATOR.join(strings)

    @classmethod
    def unpack(cls, strings: str) -> list[str]:
        return strings.split(cls.PACK_SEPARATOR)

    ##############################################

    @classmethod
    def from_args(cls, *strings: str) -> Self:
        return cls(strings)

    def __init__(self, strings: Iterable[str]) -> None:
        self._strings = list(strings)

    # def __init__(self, *strings: str | Iterable[str]) -> None:

    ##############################################
    #
    # Hashable Protocol
    #

    def __hash__(self) -> int:
        return hash(self.pack(self._strings))

    def __eq__(self, other: object) -> bool:
        return isinstance(other, StringList) and self._strings == other._strings

    ##############################################

    def __repr__(self) -> str:
        return repr(self._strings)

    def __len__(self) -> int:
        return len(self._strings)

    def __bool__(self) -> bool:
        return bool(self._strings)

    def __iter__(self) -> Iterator[str]:
        return iter(self._strings)

    def to_list(self) -> list[str]:
        return list(self._strings)

    def to_tuple(self) -> tuple[str, ...]:
        return tuple(self._strings)

    def __getitem__(self, slice: int | slice) -> str | list[str]:
        return self._strings[slice]

    def pop(self, index: int = 0) -> str:
        # Warning: default is 0 !
        return self._strings.pop(index)

####################################################################################################

class TreeMixin:

    ##############################################

    def __init__(self) -> None:
        self._childs: list[Any] = []

    ##############################################

    def __bool__(self) -> bool:
        return bool(self._childs)

    def __len__(self) -> int:
        return len(self._childs)

    def __iter__(self) -> Iterator[Any]:
        return iter(self._childs)

    ##############################################

    @property
    def childs(self) -> list[Any]:
        return list(self._childs)

    @property
    def first_child(self) -> Any:  # ruff: ignore[any-type]
        # if self._childs:
        return self._childs[0]
        # else:
        #     return None

    ##############################################

    def append_child(self, child: Any) -> None:  # ruff: ignore[any-type]
        self._childs.append(child)

    ##############################################

    def depth_first_search(
            self,
            on_node: Callable[[TreeMixin], bool] | None = None,
            on_leaf: Callable[[TreeMixin], None] | None = None,
            on_leave: Callable[[TreeMixin], None] | None = None,
            reverse: bool = False,
    ) -> None:
        go = True
        if on_node is not None:
            go = on_node(self)
        if go:
            # print('-->')
            for child in self:
                if isinstance(child, TreeMixin):
                    child.depth_first_search(on_node, on_leaf, on_leave)
                elif on_leaf is not None:
                    on_leaf(child)
            # print('<--')
            if on_leave is not None:
                on_leave(self)

####################################################################################################

class Node(TreeMixin):

    ##############################################

    def __init__(self, path: list[str]) -> None:
        super().__init__()
        self._path = path

    ##############################################

    @property
    def name(self) -> str:
        return self._path[-1]

    @property
    def path(self) -> list[str]:
        return self._path

    @property
    def path_str(self) -> str:
        return '/'.join(self._path)

    @property
    def parent_str(self) -> str:
        _ = self._path[:-1]
        if _:
            return '/'.join(_)
        return '/'

    ##############################################

    def __str__(self) -> str:
        return f"{self.path_str}: {self.childs}"

    def __repr__(self) -> str:
        return f"{self.path_str}: {self.childs}"

    ##############################################

    def xpath(self, path: str) -> list[Node]:
        # DEBUG = False
        # DEBUG = True

        if path.startswith('/'):
            path = path[1:]
            index = 0
        else:
            # relative
            index = -1
        parts = path.split('/')
        last_index = len(parts) - 1
        # if DEBUG:
        #     print(parts, last_index)

        results: list[Node] = []

        def on_node(node: Node) -> bool:
            nonlocal index
            if index == -1:
                index = 0
                return True
            # if DEBUG:
            #     indent = '    ' * index
            #     print(indent, '@', index + 1, node.path_str)
            if node.name == parts[index]:
                # if DEBUG:
                #     print(indent, '  match')
                if index == last_index:
                    # if DEBUG:
                    #     print(indent, '  found')
                    results.append(node)
                    return False
                index += 1
                return True
            return False

        def on_leave(node: Node) -> None:
            nonlocal index
            # if DEBUG:
            #     indent = '    ' * index
            #     print(indent, '<<<@', index + 1, 'leave')
            index -= 1

        self.depth_first_search(on_node, on_leave=on_leave)  # ty: ignore[invalid-argument-type]
        return results

    ##############################################

    @property
    def child_types(self) -> list:
        return list(type(_).__name__ for _ in self)

    @property
    def child_types2(self) -> list:
        def child_type(child: Any) -> str:  # ruff: ignore[any-type]
            if isinstance(child, Node):
                return child.name
            else:
                return type(child).__name__

        return list(child_type(_) for _ in self)

    def get_child(self, name: str) -> Node | None:
        for child in self:
            if isinstance(child, Node) and child.name == name:
                return child
        return None

####################################################################################################

class SchemaNode(TreeMixin):

    # key is node path
    NODES: dict[str, SchemaNode] = {}

    ##############################################

    @classmethod
    def get_node(cls, node: Node) -> SchemaNode:
        if not cls.NODES:
            # add root
            cls.NODES['/'] = SchemaNode('/')

        path_str = node.path_str
        if path_str in cls.NODES:
            return cls.NODES[path_str]
        else:
            schema_node = SchemaNode(node.name)
            cls.NODES[path_str] = schema_node
            parent = cls.NODES[node.parent_str]
            parent.append_child(schema_node)
            return schema_node

    @classmethod
    def root(cls) -> SchemaNode:
        return cls.NODES['/']

    ##############################################

    def __init__(self, name: str) -> None:
        super().__init__()
        self._name = name
        self._instances = []

    ##############################################

    @property
    def name(self) -> str:
        return self._name

    ##############################################

    def __repr__(self) -> str:
        number_of_instances = len(self._instances)
        childs = set()
        for node in self._instances:
            child_str = ', '.join(node.child_types)
            child_str = re.sub(r'Node,( Node,)+ Node', 'Node, ..., Node', child_str)
            childs.add(child_str)
        _ = ' | '.join(childs)
        return f'{self._name} #{number_of_instances} ({_})'

    ##############################################

    def link_instance(self, instance: Node) -> None:
        self._instances.append(instance)

    ##############################################

    @property
    def child_types(self) -> set[StringList]:
        return set(StringList(_.child_types2) for _ in self._instances)

####################################################################################################

class Objectifier:

    _logger = _module_logger.getChild('Objectifier')

    ##############################################

    def __init__(self, path: Path | str) -> None:
        self._logger.info(f"Load {path}")
        with open(path) as fh:
            sexpr = S.load(fh)
        self._root = cast(Node, self._walk_sexpr(sexpr))

    ##############################################

    def _walk_sexpr(self, sexpr: SexprType, path: list[str] | None = None) -> int | float | str | Node:
        """Perform a depth first search"""
        match sexpr:
            case int() | float() | str():
                return sexpr
            # case Symbol():  # match str
            #     return sexpr  # ??? .value()
            case list():
                car = S.car(sexpr)
                # Fixme: ???
                if not isinstance(car, Symbol):
                    raise ValueError(f"car is not Symbol {sexpr}")
                car = str(car)  # car is a Symbol
                cdr = S.cdr(sexpr)
                path = path.copy() if path is not None else []
                path.append(car)
                node = Node(path)
                for element in cdr:
                    child = self._walk_sexpr(element, path)
                    node.append_child(child)
                return node
            case _:
                raise ValueError(f"Invalid sexpr {sexpr}")

    ##############################################

    @property
    def root(self) -> Node:
        return self._root

    ##############################################

    def dump(self, root: Node | None = None) -> None:
        """Dump sexp structure"""
        if root is None:
            root = self._root

        def on_node(node: Node) -> bool:
            print(node.path_str)
            return True

        def on_leaf(leaf: Node) -> None:
            print(f"    {leaf}")

        root.depth_first_search(on_node, on_leaf)  # ty: ignore[invalid-argument-type]

    ##############################################

    def get_paths(self, root: Node | None = None) -> None:
        """Dump sexp path"""
        if root is None:
            root = self._root
        paths = set()

        def on_node(node: Node) -> bool:
            paths.add(node.path_str)
            return True

        root.depth_first_search(on_node)  # ty: ignore[invalid-argument-type]
        for _ in sorted(paths):
            print(_)

    ##############################################

    def get_schema(self, root: Node | None = None) -> None:
        if root is None:
            root = self._root

        def on_node(node: Node) -> bool:
            schema_node = SchemaNode.get_node(node)
            schema_node.link_instance(node)
            return True

        def on_leaf(leaf: Node) -> None:
            pass

        root.depth_first_search(on_node, on_leaf)  # ty: ignore[invalid-argument-type]
