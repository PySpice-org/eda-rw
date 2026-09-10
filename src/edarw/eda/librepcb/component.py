####################################################################################################
#
# EDA-RW — Python library to read/write EDA Sexpr file format
# Copyright (C) 2026 Fabrice SALVAIRE
# SPDX-License-Identifier: AGPL-3.0-or-later
#
####################################################################################################

####################################################################################################

__all__ = ['Component']

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

class Attribute(SexprWrapper):
    CAR = 'attribute'
    name: Positional[str]
    type: str
    unit: str
    value: str

####################################################################################################

class Signal(SexprWrapper):
    CAR = 'signal'
    uuid: Positional[UUID]
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

class Pin(SexprWrapper):
    CAR = 'pin'
    uuid: Positional[UUID]
    signal: UUID
    text: str

###################################################################################################

class Gate(SexprWrapper):
    CAR = 'gate'
    uuid: Positional[UUID]
    symbol: UUID
    position: tuple[float, float]
    rotation: float
    required: bool
    suffix: str
    pin: list[Pin]

####################################################################################################

class Variant(SexprWrapper):
    CAR = 'variant'
    uuid: Positional[UUID]
    norm: str
    name: str
    description: str
    gate: Gate

####################################################################################################

class Component(SexprWrapper):

    """Class to read a LibrePCB Component"""

    CAR = 'librepcb_component'
    uuid: Positional[UUID]
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

    ##############################################

    def __repr__(self) -> str:
        return f"Component uuid={self.uuid} name='{self.name}'"

    ##############################################

    def get_signal(self, uuid: UUID) -> Signal:
        return self._signal_map[uuid]
