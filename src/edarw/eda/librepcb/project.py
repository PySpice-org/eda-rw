####################################################################################################
#
# EDA-RW — Python library to read/write EDA Sexpr file format
# Copyright (C) 2026 Fabrice SALVAIRE
# SPDX-License-Identifier: AGPL-3.0-or-later
#
####################################################################################################

__all__ = ['Project']

####################################################################################################

import logging
import os
import re
from collections.abc import ValuesView
from datetime import datetime
from pathlib import Path
from typing import Self

from edarw.sexpr import SexprWrapper, UUID

from .common import LibreSexpr, UuidSexpr
from .circuit import Circuit
from .component import Component, Gate
from .schematic import Schematic
from .symbol import Symbol

# from rich import print

####################################################################################################

_module_logger = logging.getLogger(__name__)

LINESEP = os.linesep

####################################################################################################

class Project(UuidSexpr):

    """Class to read a LibrePCB Project"""

    CAR = 'librepcb_project_metadata'
    name: str
    author: str
    version: str
    created: datetime

    _logger = _module_logger.getChild('Project')

    ##############################################

    @classmethod
    def guess_loader(self, path: Path | str) -> type[LibreSexpr]:
        """Return the class for '(librepcb_... ...)'"""
        content = Path(path).read_text()
        match = re.match(r'^\(([a-z_]+)\s', content[:50])
        if match:
            car = match.group(1)
            try:
                return SexprWrapper.cls_for_car(car)
            except KeyError:
                raise NotImplementedError(f"Car is {car}")  # ruff: ignore[raise-without-from-inside-except]
        else:
            raise ValueError(f"This file '{path}' doesn't look like a .lp file:{LINESEP * 2}{content[:100]}")

    ##############################################

    @classmethod
    def load(self, path: Path | str) -> Self:  # ty: ignore[invalid-method-override]
        project_path = Path(path)
        metadata_path = project_path / 'project/metadata.lp'
        return super().load(metadata_path, project_path=project_path)

    ##############################################

    def __init__(self, sexpr: list, project_path: Path) -> None:
        super().__init__(sexpr)
        self._project_path = project_path
        self._circuit: Circuit | None = None
        self._schematic: Schematic | None = None
        self._components: dict[UUID, Component] = {}
        self._symbols: dict[UUID, Symbol] = {}
        self._load_library()

    ##############################################

    @property
    def project_path(self) -> Path:
        return self._project_path

    ##############################################

    def _load_library(self) -> None:
        library_path = self._project_path / 'library'
        cmp_path = library_path / 'cmp'
        for component_dir in cmp_path.iterdir():
            # component_uuid = component_dir.name
            component_path = component_dir / 'component.lp'
            component = Component.load(component_path, self)
            self._components[component.uuid] = component
        sym_path = library_path / 'sym'
        for symbol_dir in sym_path.iterdir():
            # symbol_uuid = symbol_dir.name
            symbol_path = symbol_dir / 'symbol.lp'
            symbol = Symbol.load(symbol_path, self)
            self._symbols[symbol.uuid] = symbol
        # self._gate_map = {}
        # for component in self._components.values():
        #     for variant in component.variant:
        #         gate = variant.gate
        #         self._gate_map[gate.uuid] = gate

    def component(self, uuid: UUID) -> Component:
        return self._components[uuid]

    @property
    def components(self) -> ValuesView[Component]:
        return self._components.values()

    def symbol(self, uuid: UUID) -> Symbol:
        return self._symbols[uuid]

    @property
    def symbols(self) -> ValuesView[Symbol]:
        return self._symbols.values()

    # def gate(self, uuid: UUID) -> Gate:
    #     return self._gate_map[uuid]

    ##############################################

    @property
    def circuit(self) -> Circuit:
        if self._circuit is None:
            circuit_path = self._project_path / 'circuit/circuit.lp'
            self._circuit = Circuit.load(circuit_path, self)
        return self._circuit

    ##############################################

    @property
    def schematic(self) -> Schematic:
        if self._schematic is None:
            schematic_path = self._project_path / 'schematics/main/schematic.lp'
            self._schematic = Schematic.load(schematic_path, self)
        return self._schematic
