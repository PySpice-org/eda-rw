####################################################################################################
#
# KiCad-RW — Python library to read/write KiCad Sexpr file format
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
from typing import Any, Iterator

import sexpdata
from sexpdata import car, cdr, Symbol

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

def car_value(_):
    return car(_).value()

####################################################################################################

class TreeMixin:

    ##############################################

    def __init__(self) -> None:
        self._childs = []

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
    def first_child(self) -> Any:
        # if self._childs:
        return self._childs[0]
        # else:
        #     return None

    ##############################################

    def append_child(self, child: Any) -> None:
        self._childs.append(child)

    ##############################################

    def depth_first_search(self, on_node=None, on_leaf=None, on_leave=None) -> None:
        go = True
        if on_node:
            go = on_node(self)
        if go:
            # print('-->')
            for child in self:
                if isinstance(child, Node):
                    child.depth_first_search(on_node, on_leaf, on_leave)
                elif on_leaf:
                    on_leaf(child)
            # print('<--')
            if on_leave:
                on_leave(self)

####################################################################################################

class Node(TreeMixin):

    ##############################################

    def __init__(self, path: str) -> None:
        super().__init__()
        self._path = path

    ##############################################

    @property
    def name(self) -> str:
        return self._path[-1]

    @property
    def path(self) -> str:
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

    def xpath(self, path: str):

        DEBUG = False

        if path.startswith('/'):
            path = path[1:]
            index = 0
        else:
            # relative
            index = -1
        parts = path.split('/')
        last_index = len(parts) -1
        if DEBUG:
            print(parts, last_index)

        results = []

        def on_node(node):
            nonlocal index
            if index == -1:
                index = 0
                return True
            if DEBUG:
                indent = '    '*index
                print(indent, '@', index+1, node.path_str)
            if node.name == parts[index]:
                if DEBUG:
                    print(indent, '  match')
                if index == last_index:
                    if DEBUG:
                        print(indent, '  found')
                    results.append(node)
                    return False
                index += 1
                return True
            return False

        def on_leave(node):
            nonlocal index
            if DEBUG:
                indent = '    '*index
                print(indent, '<<<@', index+1, 'leave')
            index -= 1

        self.depth_first_search(on_node, on_leave=on_leave)
        return results

####################################################################################################

class SchemaNode(TreeMixin):

    NODES = {}

    ##############################################

    @classmethod
    def get_node(cls, node: None) -> 'SchemaNode':
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
            child_str = '/'.join([type(_).__name__ for _ in node])
            child_str = re.sub(r'Node\/(Node\/)+Node', 'Node/.../Node', child_str)
            childs.add(child_str)
        return f'{self._name} #{number_of_instances} {childs}'

    ##############################################

    def link_instance(self, instance: Node) -> None:
        self._instances.append(instance)

####################################################################################################

class Objectifier:

    _logger = _module_logger.getChild('Objectifier')

    ##############################################

    def __init__(self, path: str) -> None:
        self._logger.info(f"Load {path}")
        with open(path) as fh:
            sexpr = sexpdata.load(fh)
        self._root = self._walk_sexpr(sexpr)

    ##############################################

    @property
    def root(self) -> Node:
        return self._root

    ##############################################

    def dump(self, root: Node = None) -> None:
        """Sump sexp structure"""
        if root is None:
            root = self._root
        def on_node(node):
            print(node.path_str)
            return True
        def on_leaf(leaf):
            print(f"    {leaf}")
        root.depth_first_search(on_node, on_leaf)

    ##############################################

    def get_paths(self, root: Node = None) -> None:
        """Dump sexp path"""
        if root is None:
            root = self._root
        paths = set()
        def on_node(node):
            paths.add(node.path_str)
            return True
        root.depth_first_search(on_node)
        for _ in sorted(paths):
            print(_)

    ##############################################

    def get_schema(self, root: Node = None) -> None:
        if root is None:
            root = self._root
        def on_node(node):
            schema_node = SchemaNode.get_node(node)
            schema_node.link_instance(node)
            return True
        def on_leaf(leaf):
            pass
        root.depth_first_search(on_node, on_leaf)

    ##############################################

    def _walk_sexpr(self, sexpr, path=[]):
        """Perform a depth first search"""
        if isinstance(sexpr, (str, int, float)):
            return sexpr
        elif isinstance(sexpr, Symbol):
            return sexpr   # ??? .value()
        elif isinstance(sexpr, list):
            _car = car(sexpr)
            if isinstance(_car, Symbol):
                _car = str(_car)
            else:
                _car.value()
            _cdr = cdr(sexpr)
            path = path.copy()
            path.append(_car)
            node = Node(path)
            for element in _cdr:
                child = self._walk_sexpr(element, path)
                node.append_child(child)
            return node
        else:
            raise ValueError()
