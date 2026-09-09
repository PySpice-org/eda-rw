####################################################################################################
#
# EDA-RW — Python library to read/write EDA Sexpr file format
# Copyright (C) 2026 Fabrice SALVAIRE
# SPDX-License-Identifier: AGPL-3.0-or-later
#
####################################################################################################

__all__ = [
    'Positional',
    'SexprWrapper',
    'UUID',
]

####################################################################################################

import annotationlib
import builtins
import logging
from pathlib import Path
from typing import _SpecialForm, Self

import sexpdata as S
from rich import print
from sexpdata import Symbol

####################################################################################################

_module_logger = logging.getLogger(__name__)

type UUID = str

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

    _logger = _module_logger.getChild('SexprWrapper')

    ##############################################

    @classmethod
    def load(cls, path: Path | str) -> Self:
        print(f"Load {path}")
        with Path(path).open() as fh:
            sepr = S.load(fh)
        return cls(sepr)

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
                    case builtins.str | builtins.bool | builtins.int | builtins.float:
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
