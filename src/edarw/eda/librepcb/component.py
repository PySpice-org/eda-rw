####################################################################################################
#
# EDA-RW — Python library to read/write EDA Sexpr file format
# Copyright (C) 2026 Fabrice SALVAIRE
# SPDX-License-Identifier: AGPL-3.0-or-later
#
####################################################################################################

__all__ = ['Component']

####################################################################################################

import logging
from datetime import datetime
from pathlib import Path
from typing import TYPE_CHECKING, Self

from rich import print

from edarw.sexpr import UUID, Positional

from .common import LibreSexpr, UuidSexpr

if TYPE_CHECKING:
    from .project import Project

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

class Attribute(LibreSexpr):
    CAR = 'attribute'
    name: Positional[str]
    type: str
    unit: str
    value: str

####################################################################################################

class Signal(UuidSexpr):
    CAR = 'signal'
    name: str
    role: str
    required: bool
    negated: bool
    clock: bool
    forced_net: str  # Fixme: ???

    ##############################################

    def __repr__(self) -> str:
        return f"Signal {self.uuid} name='{self.name}' role='{self.role}'"

####################################################################################################

class Pin(UuidSexpr):
    CAR = 'pin'
    signal: UUID
    text: str

###################################################################################################

class Gate(UuidSexpr):
    CAR = 'gate'
    symbol: UUID
    position: tuple[float, float]
    rotation: int
    required: bool
    suffix: str
    pin: list[Pin] = None  # ty: ignore[invalid-assignment]

####################################################################################################

class Variant(UuidSexpr):
    CAR = 'variant'
    norm: str
    name: str
    description: str
    gate: Gate

####################################################################################################

class Component(UuidSexpr):

    """Class to read a LibrePCB Component"""

    CAR = 'librepcb_component'
    name: list[str]  # Fixme: local
    description: list[str]
    keywords: str
    author: str
    version: str
    created: datetime
    deprecated: bool
    generated_by: str
    category: str
    schematic_only: bool
    default_value: str
    prefix: str
    attribute: list[Attribute] = None  # ty: ignore[invalid-assignment]
    signal: list[Signal] = None  # ty: ignore[invalid-assignment]
    variant: list[Variant] = None  # ty: ignore[invalid-assignment]

    _logger = _module_logger.getChild('Component')

    ##############################################

    @classmethod
    def load(self, path: Path | str, project: Project) -> Self:  # ty: ignore[invalid-method-override]
        return super().load(path, project=project)

    ##############################################

    def __init__(self, sexpr: list, project: Project) -> None:
        super().__init__(sexpr)
        self._project = project
        self._signal_map: dict[UUID, Signal] = {_.uuid: _ for _ in self.signal}
        self._variant_map: dict[UUID, Variant] = {_.uuid: _ for _ in self.variant}

    ##############################################

    def get_signal(self, uuid: UUID) -> Signal:
        return self._signal_map[uuid]

    def get_variant(self, uuid: UUID) -> Variant:
        return self._variant_map[uuid]

    ##############################################

    def __repr__(self) -> str:
        return f"Component uuid={self.uuid} name='{self.name}'"
