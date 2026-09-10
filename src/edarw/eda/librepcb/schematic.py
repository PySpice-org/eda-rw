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
from typing import TYPE_CHECKING, Self

from edarw.sexpr import UUID, Positional, SexprWrapper

from rich import print

if TYPE_CHECKING:
    from .project import Project

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

class Text(SexprWrapper):
    CAR = 'text'
    uuid: Positional[UUID]
    layer: str
    height: float
    align: list[str]
    position: tuple[float, float]
    rotation: float
    lock: bool
    value: str

####################################################################################################

class Symbol(SexprWrapper):
    CAR = 'symbol'
    uuid: Positional[UUID]
    component: UUID
    lib_gate: UUID
    text: list[Text] = None  # ty: ignore[invalid-assignment]

####################################################################################################

class Grid(SexprWrapper):
    CAR = 'grid'
    interval: float
    unit: str

####################################################################################################

class From(SexprWrapper):
    CAR = 'from'
    symbol: UUID = None
    pin: UUID = None
    junction: UUID = None

class To(SexprWrapper):
    CAR = 'to'
    symbol: UUID = None
    pin: UUID = None
    junction: UUID = None

####################################################################################################

class Line(SexprWrapper):
    CAR = 'line'
    RENAMING = {'from_': 'from'}
    uuid: Positional[UUID]
    width: float
    from_: From
    to: To

####################################################################################################

class Junction(SexprWrapper):
    CAR = 'junction'
    uuid: Positional[UUID]
    position: tuple[float, float]

####################################################################################################

class NetSegment(SexprWrapper):
    CAR = 'netsegment'
    uuid: Positional[UUID]
    net: UUID
    junction: list[Junction] = None  # ty: ignore[invalid-assignment]
    line: list[Line]

####################################################################################################

class Schematic(SexprWrapper):

    """Class to read a LibrePCB Symbol"""

    CAR = 'librepcb_schematic'
    uuid: Positional[UUID]
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

    ##############################################

    def __repr__(self) -> str:
        return f"Schematic uuid={self.uuid} name='{self.name}'"
