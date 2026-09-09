####################################################################################################
#
# EDA-RW — Python library to read/write EDA Sexpr file format
# Copyright (C) 2026 Fabrice SALVAIRE
# SPDX-License-Identifier: AGPL-3.0-or-later
#
####################################################################################################

__all__ = ['Circuit']

####################################################################################################

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Self, cast

from edarw.sexpr import UUID, Positional, SexprWrapper

# from rich import print

if TYPE_CHECKING:
    from . import component
    from .project import Project

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

    def __init__(self, sexpr: list, indent_level: int, parent: Circuit) -> None:
        super().__init__(sexpr, indent_level, parent)
        self._signals: list[Signal] = []

    ##############################################

    def __repr__(self) -> str:
        return f"Net uuid={self.uuid} name='{self.name}' netclass={self.netclass}"

    ##############################################

    @property
    def signals(self) -> list[Signal]:
        # Fixme: immutable
        return self._signals

####################################################################################################

class Attribute(SexprWrapper):
    CAR = 'attribute'
    name: Positional[str]
    type: str
    unit: str
    value: str

    ##############################################

    def __repr__(self) -> str:
        return f"Attribute name='{self.name}' type='{self.type}' value='{self.value}'  unit='{self.unit}'"

####################################################################################################

class Signal(SexprWrapper):
    CAR = 'signal'
    uuid: Positional[UUID]
    net: UUID  # Fixme: can be 'none'

    ##############################################

    def __repr__(self) -> str:
        return f"Signal {self.uuid} on net {self.net}"

    ##############################################

    # @property
    # def parent(self) -> Component:
    #     return cast(Component, self._parent)

    @property
    def component(self) -> Component:
        return cast(Component, self._parent)

    ##############################################

    @property
    def signal_def(self) -> component.Signal:
        component = self.component.component_def
        return component.get_signal(self.uuid)

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

    # @property
    # def parent(self) -> Circuit:
    #     return cast(Circuit, self._parent)

    @property
    def circuit(self) -> Circuit:
        return cast(Circuit, self._parent)

    ##############################################

    def __repr__(self) -> str:
        return f"Component uuid={self.uuid} name='{self.name}' value='{self.value}'"

    ##############################################

    @property
    def component_def(self) -> component.Component:
        return self.circuit.project.component(self.lib_component)

####################################################################################################

class Circuit(SexprWrapper):

    """Class to read a LibrePCB Circuit"""

    CAR = 'librepcb_circuit'
    variant: Variant
    netclass: list[Netclass]
    net: list[Net]
    component: list[Component]

    _logger = _module_logger.getChild('Circuit')

    ##############################################

    @classmethod
    def load(self, path: Path | str, project: Project) -> Self:  # ty: ignore[invalid-method-override]
        return super().load(path, project=project)

    ##############################################

    def __init__(self, sexpr: list, project: Project) -> None:
        super().__init__(sexpr)
        self._project = project
        self._net_map = {_.uuid: _ for _ in self.net}
        for component in self.component:
            for signal in component.signal:
                if signal.net != 'none':
                    net = self.get_net(signal.net)
                    net._signals.append(signal)

    ##############################################

    def get_net(self, uuid: UUID) -> Net:
        return self._net_map[uuid]

    ##############################################

    @property
    def project(self) -> Project:
        return self._project
