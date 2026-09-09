####################################################################################################
#
# KiCad-RW — Python library to read/write KiCad Sexpr file format
# Copyright (C) 2021 Fabrice SALVAIRE
# SPDX-License-Identifier: AGPL-3.0-or-later
#
####################################################################################################

####################################################################################################

__all__ = [
    'KiCadSchema',
]

####################################################################################################

import logging
from collections.abc import Iterable, Iterator
from itertools import combinations
from typing import Any

from rich import print

from kicadrw.geometry import EuclidianMatrice, Position, PositionAngle, Vector

# Fixme: use sexpdata ???
from kicadrw.sexp.deprecated.sexpression import Sexpression, car_value, cdr

####################################################################################################

_module_logger = logging.getLogger(__name__)

type UUID = str

####################################################################################################

def to_bool(value: str) -> bool:
    # return True if value == 'true' else False
    match value:
        case 'true':
            return True
        case 'false':
            return False
        case _:
            raise ValueError(f"Bad bool value {value}")

####################################################################################################

class UuidMixin:

    ##############################################

    def __init__(self, uuid: UUID) -> None:
        self._uuid = uuid

    ##############################################

    @property
    def uuid(self) -> UUID:
        return self._uuid

####################################################################################################

class NameMixin:

    ##############################################

    def __init__(self, name: str) -> None:
        self._name = name

    ##############################################

    # def __hash__(self) -> int:
    #     return hash((self.__class__.__name__, self._name))

    ##############################################

    @property
    def name(self) -> str:
        return self._name

    # @property
    # def full_name(self) -> str:
    #     return f"{self.__class__.__name__} {self._name}"

####################################################################################################

class Net(UuidMixin, NameMixin):

    """Class to implement a net"""

    ##############################################

    def __init__(self, uuid: UUID, name: str, auto: bool, netclass: str) -> None:
        UuidMixin.__init__(self, uuid)
        NameMixin.__init__(self, name)
        self._auto = auto
        self._netclass = netclass

    ##############################################

    def __repr__(self) -> str:
        return f"Net {self.uuid} / {self.name}"

####################################################################################################

class Signal(UuidMixin):

    def __init__(self, uuid: UUID, net: UUID) -> None:
        UuidMixin.__init__(self, uuid)
        self._net = net

    ##############################################

    def __repr__(self) -> str:
        return f"Signal {self.uuid} on net {self._net}"

####################################################################################################

class Component(UuidMixin, NameMixin):

    """Class to implement a net"""

    ##############################################

    def __init__(
            self,
            uuid: UUID,
            name: str,
            lib_component: UUID,
            lib_variant: UUID,
            value: str,
            lock_assembly: bool,
            signals: list[Signal],
    ) -> None:
        UuidMixin.__init__(self, uuid)
        NameMixin.__init__(self, name)
        self.lib_component = lib_component
        self.lib_variant = lib_variant
        self.value = value
        self.lock_assembly = lock_assembly
        self.signal = signals

    ##############################################

    def __repr__(self) -> str:
        return f"Component {self.uuid} / {self.name}"

####################################################################################################

class Circuit(Sexpression):

    """Class to read a KiCad Schema"""

    _logger = _module_logger.getChild('Circuit')

    GROUND_SYMBOLS = (
        # 'spice-ngspice:0',
        'power:GND',
    )

    ##############################################

    def __init__(self, path) -> None:
        # self._symbol_libs = {}
        # self._wires: list[Wire] = []
        # self._buses: list[Bus] = []
        # self._junctions: list[Junction] = []
        # self._no_connections: list[NoConnect] = []
        # self._bus_entries: list[BusEntry] = []
        # self._labels: list[Label] = []
        # self._global_labels: list[GlobalLabel] = []
        # self._hierarchical_labels: list[HierarchicalLabel] = []
        # self._symbols: list[Symbol] = []
        # self._sheets: list[Sheet] = []

        self._read(path)

    ##############################################

    def _read(self, path: str) -> None:
        self._logger.info(f"Load LibrePCB circuit {path}")
        s_data = self.load(path)

        if car_value(s_data) != 'librepcb_circuit':
            raise ValueError()

        for sexpr in cdr(s_data):
            print()
            _car_value = car_value(sexpr)
            match str(_car_value):
                case 'variant':
                    pass
                case 'netclass':
                    pass
                case 'net':
                    _, d = self.to_dict(sexpr)
                    uuid = self.sattr(d)
                    net = Net(
                        uuid,
                        d['name'],
                        to_bool(d['auto']),
                        d['netclass'],
                    )
                    print(net)
                case 'component':
                    _, d = self.to_dict(sexpr)
                    uuid = self.sattr(d)
                    self.fix_key_as_list(d, 'signal', 'signals')
                    print(d)
                    signals = [Signal(self.sattr(_), _['net']) for _ in d['signals']] if 'signals' in d else []
                    component = Component(
                        uuid,
                        d['name'],
                        d['lib_component'],
                        d['lib_variant'],
                        d['value'],
                        to_bool(d['lock_assembly']),
                        signals,
                    )
                    print(component)
                case _:
                    raise ValueError(f'Unknown car {_car_value}')
