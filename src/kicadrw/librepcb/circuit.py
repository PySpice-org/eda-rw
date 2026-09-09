####################################################################################################
#
# KiCad-RW — Python library to read/write KiCad Sexpr file format
# Copyright (C) 2021 Fabrice SALVAIRE
# SPDX-License-Identifier: AGPL-3.0-or-later
#
####################################################################################################

####################################################################################################

__all__ = []

####################################################################################################

import annotationlib
import builtins
import logging
from pathlib import Path
from typing import _SpecialForm

# Fixme: use sexpdata ???
# from kicadrw.sexp.deprecated.sexpression import Sexpression, car_value, cdr
import sexpdata as S
from rich import print
from sexpdata import Symbol

####################################################################################################

def get_value(_: Symbol) -> str:
    """Return `component` for `Symbol('component')`"""
    if isinstance(_, Symbol):
        return str(_)
    else:
        raise ValueError(f"Invalid type {_.type} = {_}")

def car_value(_: tuple | list) -> str:
    """Return `component` for `(Symbol('component' . cdr))`"""
    return get_value(S.car(_))

####################################################################################################

_module_logger = logging.getLogger(__name__)

type UUID = str

class PositionalField:
    def __init__(self, type_) -> None:
        self.type = type_

    def __repr__(self) -> str:
        return f"PositionalField[{self.type}]"

@_SpecialForm  # ty: ignore[too-many-positional-arguments]
def Positional(self, type_):
    return PositionalField(type_)

####################################################################################################

class SexprWrapper:

    CAR: str

    ##############################################

    @staticmethod
    def _to_bool(value: str) -> bool:
        # return True if value == 'true' else False
        match value:
            case 'true':
                return True
            case 'false':
                return False
            case _:
                raise ValueError(f"Bad bool value {value}")

    @classmethod
    def _to_python(cls, type_, value):
        # print(f"  to Python '{value}' <{type(value)}> -> <{type_}>")
        match value:
            case list():
                if len(value) == 1:
                    return cls._to_python(type_, value[0])
            case Symbol():
                match type_:
                    case builtins.str | builtins.bool:
                        return cls._to_python(type_, value.value())
                # Fixme: how to write case ???
                if type_ == UUID:
                    return cls._to_python(type_, value.value())
        match type_:
            case builtins.bool:
                return cls._to_bool(value)
            case _:
                return value

    ##############################################

    def __init__(self, sexpr, indent_level: int = 0) -> None:
        indent = ' ' * 8 * indent_level
        cls = self.__class__
        annotations = annotationlib.get_annotations(cls)
        print(f"{indent}CAR = {self.CAR} {annotations}")
        if not indent_level:
            print(sexpr)
        if car_value(sexpr) != self.CAR:
            raise ValueError(f"CAR is {car_value} instead of {self.CAR}")
        cdr = S.cdr(sexpr)
        # for field, type in annotations.items():
        #     try:
        #         default_value = getattr(cls, field)
        #         # print(f"{field} {type} = '{default_value}'")
        #         setattr(self, field, kwargs.get(field, default_value))
        #     except AttributeError:
        #         print(f"{field} {type}")
        #         if field in kwargs:
        #             _ = kwargs.get(field)
        #             match type:
        #                 case bool():
        #                     value = self._to_bool(cast(str, _))
        #                 case _:
        #                     value = _
        #             setattr(self, field, value)
        #         else:
        #             raise NameError(f"field {field} is missing")  # ruff: ignore[raise-without-from-inside-except]

        def _setattr(field, value):
            print(f"{indent}  .{field} = {value} <{type(value)}>")
            setattr(self, field, value)

        def _append(field, obj_type, sexpr):
            value = obj_type(sexpr, indent_level + 1)
            print(f"{indent}  .{field} += {value} <{type(value)}>")
            getattr(self, field).append(value)

        for field, type_ in annotations.items():
            field_sexpr = cdr.pop(0) if cdr else None
            try:
                default_value = getattr(cls, field)
                has_default = True
                print(f"{field}<{type_}> = {field_sexpr} = '{default_value}'")
            except AttributeError:
                has_default = False
                print(f"{field}<{type_}> = {field_sexpr}")
            if isinstance(type_, PositionalField):
                value = self._to_python(type_.type, field_sexpr)
                _setattr(field, value)
            else:
                is_list = hasattr(type_, '__origin__') and type_.__origin__ == builtins.list
                # if is_list:
                #     print('  is list')
                if field_sexpr is None:
                    car = None
                    field_cdr = None
                else:
                    car = car_value(field_sexpr)
                    field_cdr = S.cdr(field_sexpr)
                if car == field:
                    # print('  field match')
                    if is_list:
                        if not hasattr(self, field) or getattr(self, field) is None:
                            setattr(self, field, [])
                        obj_type = type_.__args__[0]
                        _append(field, obj_type, field_sexpr)
                        while cdr and car_value(cdr[0]) == field:
                            field_sexpr = cdr.pop(0)
                            _append(field, obj_type, field_sexpr)
                    else:
                        value = self._to_python(type_, field_cdr)
                        _setattr(field, value)
                else:
                    if has_default:
                        # print('  set default value')
                        _setattr(field, default_value)
                    else:
                        raise NameError(f"field {field} is missing")

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

class Circuit:

    """Class to read a KiCad Schema"""

    _logger = _module_logger.getChild('Circuit')

    GROUND_SYMBOLS = (
        # 'spice-ngspice:0',
        'power:GND',
    )

    ##############################################

    @classmethod
    def load(cls, path: Path | str) -> list:
        with Path(path).open() as fh:
            _ = S.load(fh)
        return _

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

        for sexpr in S.cdr(s_data):
            print('-' * 50)
            car = car_value(sexpr)
            match str(car):
                case 'variant':
                    pass
                case 'netclass':
                    pass
                case 'net':
                    net = Net(sexpr)
                    print(net)
                case 'component':
                    component = Component(sexpr)
                    print(component)
                case _:
                    raise ValueError(f'Unknown car {_car_value}')
