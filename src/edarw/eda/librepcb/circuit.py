####################################################################################################
#
# EDA-RW — Python library to read/write EDA Sexpr file format
# Copyright (C) 2021 Fabrice SALVAIRE
# SPDX-License-Identifier: AGPL-3.0-or-later
#
####################################################################################################

####################################################################################################

__all__ = []

####################################################################################################

import logging

import sexpdata as S
from rich import print

from edarw.sexpr import UUID, Positional, SexprWrapper

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

class Variant(SexprWrapper):
    CAR = 'variant'
    uuid: Positional[UUID]
    name: str
    description: str

####################################################################################################

class Netclass(SexprWrapper):
    CAR = 'netclass'
    uuid: Positional[UUID]
    name: str
    default_trace_width: str
    default_via_drill_diameter: str
    min_copper_copper_clearance: float
    min_copper_width: float
    min_via_drill_diameter: float

####################################################################################################

class Net(SexprWrapper):

    """Class to implement a net"""

    CAR = 'net'
    uuid: Positional[UUID]
    auto: bool
    name: str
    netclass: UUID

    ##############################################

    def __repr__(self) -> str:
        return f"Net {self.uuid} / {self.name}"

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
    net: UUID  # Fixme: can be 'none'

    ##############################################

    def __repr__(self) -> str:
        return f"Signal {self.uuid} on net {self.net}"

####################################################################################################

class Component(SexprWrapper):

    """Class to implement a net"""

    CAR = 'component'
    uuid: Positional[UUID]
    lib_component: UUID
    lib_variant: UUID
    name: str
    value: str
    lock_assembly: bool
    attribute: list[Attribute] = None  # ty: ignore[invalid-assignment]
    signal: list[Signal] = None  # ty: ignore[invalid-assignment]

    ##############################################

    def __repr__(self) -> str:
        return f"Component {self.uuid} / {self.name}"

####################################################################################################

class Circuit(SexprWrapper):

    """Class to read a KiCad Schema"""

    CAR = 'librepcb_circuit'
    variant: Variant
    netclass: list[Netclass]
    net: list[Net]
    component: list[Component]

    _logger = _module_logger.getChild('Circuit')
