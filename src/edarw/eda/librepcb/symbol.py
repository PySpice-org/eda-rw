####################################################################################################
#
# EDA-RW — Python library to read/write EDA Sexpr file format
# Copyright (C) 2026 Fabrice SALVAIRE
# SPDX-License-Identifier: AGPL-3.0-or-later
#
####################################################################################################

__all__ = ['Symbol']

####################################################################################################

import logging
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Self

from edarw.sexpr import UUID, Positional, SexprWrapper

from rich import print

if TYPE_CHECKING:
    from .project import Project

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

class Pin(SexprWrapper):
    CAR = 'pin'
    uuid: Positional[UUID]
    position: tuple[float, float] = None  # ty: ignore[invalid-assignment]
    rotation: float = None  # ty: ignore[invalid-assignment]
    length: float = None  # ty: ignore[invalid-assignment]
    name_position: tuple[float, float] = None  # ty: ignore[invalid-assignment]
    name_rotation: float = None  # ty: ignore[invalid-assignment]
    name_height: float = None  # ty: ignore[invalid-assignment]
    name_align: list[str] = None  # ty: ignore[invalid-assignment]

###################################################################################################

class Vertex(SexprWrapper):
    CAR = 'vertex'
    position: tuple[float, float]
    angle: float

###################################################################################################

class Polygon(SexprWrapper):
    CAR = 'polygon'
    uuid: Positional[UUID]
    layer: str
    width: float
    fill: bool
    grab_area: bool
    vertex: list[Vertex]

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

    """Class to read a LibrePCB Symbol"""

    CAR = 'librepcb_symbol'
    uuid: Positional[UUID]
    name: str
    description: list[str]
    keywords: str
    author: str
    version: str
    created: datetime
    deprecated: bool
    generated_by: str
    category: str
    grid_interval: float
    pin: list[Pin] = None  # ty: ignore[invalid-assignment]
    polygon: list[Polygon] = None  # ty: ignore[invalid-assignment]
    text: list[Text] = None  # ty: ignore[invalid-assignment]
    approved: list[str] = None  # ty: ignore[invalid-assignment]

    _logger = _module_logger.getChild('Symbol')

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
        return f"Symbol uuid={self.uuid} name='{self.name}'"
