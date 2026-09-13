####################################################################################################
#
# EDA-RW — Python library to read/write EDA Sexpr file format
# Copyright (C) 2026 Fabrice SALVAIRE
# SPDX-License-Identifier: AGPL-3.0-or-later
#
####################################################################################################

__all__ = ['Schematic']

####################################################################################################

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Self, cast

from rich import print

from edarw.geometry import Position as gPosition, EuclidianMatrix
from edarw.sexpr import UUID

from .common import LibreSexpr, Position, UuidSexpr

if TYPE_CHECKING:
    from .component import Component, Gate
    from .project import Project

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

class Text(UuidSexpr):
    CAR = 'text'
    layer: str
    height: float
    align: list[str]
    position: tuple[float, float]
    rotation: int
    lock: bool
    value: str

####################################################################################################

class Symbol(UuidSexpr):
    CAR = 'symbol'
    component: UUID  # -> Circuit.component
    lib_gate: UUID  # -> Component.gate
    position: tuple[float, float]
    rotation: int
    mirror: bool
    text: list[Text] = None  # ty: ignore[invalid-assignment]

    ##############################################

    @property
    def schematic(self) -> Schematic:
        return cast(Schematic, self._parent)

    @property
    def project(self) -> Project:
        return self.schematic.project

    ##############################################

    # @property
    # def gate(self) -> Gate:
    #     return self.project.gate(self.lib_gate)

####################################################################################################

class Grid(LibreSexpr):
    CAR = 'grid'
    interval: float
    unit: str

####################################################################################################

class FromMixin(LibreSexpr):
    symbol: UUID = None  # ty: ignore[invalid-assignment]
    pin: UUID = None  # ty: ignore[invalid-assignment]
    junction: UUID = None  # ty: ignore[invalid-assignment]

    @property
    def is_junction(self) -> bool:
        return self.junction is not None

    @property
    def is_pin(self) -> bool:
        return self.junction is None

    @property
    def position(self) -> gPosition:
        if self.is_junction:
            position = self.junction_obj.position_obj
            # print('junction', position)
        else:
            symbol = self.symbol_obj
            _ = self.pin_obj
            pin = _['symbol.Pin'] if isinstance(_, dict) else _
            position = pin.position_obj * EuclidianMatrix.rotation(symbol.rotation)
            position += symbol.position_obj
            # print('symbol', position, point.symbol_obj.to_json(), pin.to_json())
        return position

class From(FromMixin):
    CAR = 'from'

class To(FromMixin):
    CAR = 'to'

####################################################################################################

class Line(UuidSexpr):
    CAR = 'line'
    RENAMING = {'from_': 'from'}
    width: float
    from_: From
    to: To

####################################################################################################

class Junction(UuidSexpr):
    CAR = 'junction'
    position: tuple[float, float]

####################################################################################################

class NetSegment(UuidSexpr):
    CAR = 'netsegment'
    net: UUID
    junction: list[Junction] = None  # ty: ignore[invalid-assignment]
    line: list[Line]

    ##############################################

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._junction_map = {_.uuid: _ for _ in self.junction}

    ##############################################

    def get_jonction(self, uuid: UUID) -> Junction:
        return self._junction_map[uuid]

####################################################################################################

class Schematic(UuidSexpr):

    """Class to read a LibrePCB Symbol"""

    CAR = 'librepcb_schematic'
    name: str
    grid: Grid
    symbol: list[Symbol] = None  # ty: ignore[invalid-assignment]
    netsegment: list[NetSegment] = None  # ty: ignore[invalid-assignment]

    _logger = _module_logger.getChild('Schematic')

    ##############################################

    @classmethod
    def load(self, path: Path | str, project: Project) -> Self:  # ty: ignore[invalid-method-override]
        return super().load(path, project=project)

    ##############################################

    def __init__(self, sexpr: list, project: Project) -> None:
        super().__init__(sexpr)
        self._project = project
        self._symbol_map = {_.uuid: _ for _ in self.symbol}
        self._netsegment_map = {_.uuid: _ for _ in self.netsegment}

    ##############################################

    @property
    def project(self) -> Project:
        return self._project

    ##############################################

    def get_symbol(self, uuid: UUID) -> Symbol:
        return self._symbol_map[uuid]

    def get_netsegment(self, uuid: UUID) -> NetSegment:
        return self._netsegment_map[uuid]

    ##############################################

    def __repr__(self) -> str:
        return f"Schematic uuid={self.uuid} name='{self.name}'"
