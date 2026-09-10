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
import datetime
import logging
from inspect import isclass
from pathlib import Path
from typing import Self, _SpecialForm

import sexpdata as S
from rich import print
from sexpdata import Symbol

####################################################################################################

_module_logger = logging.getLogger(__name__)

type UUID = str

####################################################################################################

DEBUG = False
# DEBUG = True

def debug_print(*args) -> None:
    if DEBUG:
        print(*args)

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
    RENAMING: dict[str, str] = {}

    _logger = _module_logger.getChild('SexprWrapper')

    ##############################################

    def __init_subclass__(cls) -> None:
        cls.IRENAMING = {b: a for a, b in cls.RENAMING.items()}

    ##############################################

    @classmethod
    def load(cls, path: Path | str, **kwargs) -> Self:
        cls._logger.info(f"Load {path}")
        with Path(path).open() as fh:
            sepr = S.load(fh)
        return cls(sepr, **kwargs)

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

    def _to_python(self, type_, value, indent_level):
        # debug_print(f"  to Python '{value}' <{type(value)}> -> <{type_}>")
        match value:
            case list():
                if len(value) == 1:
                    return self._to_python(type_, value[0], indent_level)
            case Symbol():
                match type_:
                    case builtins.str | builtins.bool | builtins.int | builtins.float:
                        return self._to_python(type_, value.value(), indent_level)
                # Fixme: how to write case ???
                if type_ == UUID:
                    return self._to_python(type_, value.value(), indent_level)
        match type_:
            case builtins.bool:
                return self._to_bool(value)
            case datetime.datetime:  # datetime. is required by Python...
                return datetime.datetime.fromisoformat(value)
            case _:
                return value

    ##############################################

    def __init__(self, sexpr: list, indent_level: int = 0, parent: object | None = None) -> None:
        # Fixme: attribute are not getter !
        self._parent = parent
        indent = ' ' * 8 * indent_level
        cls = self.__class__
        annotations = annotationlib.get_annotations(cls)
        debug_print(f"{indent}CAR = {self.CAR} {annotations}")
        if not indent_level:
            debug_print(sexpr)
        car = car_value(sexpr)
        if car != self.CAR:
            raise ValueError(f"CAR is {car} instead of {self.CAR}")
        cdr_orig = S.cdr(sexpr)
        cdr = list(cdr_orig)

        def _setattr(field, value):
            debug_print(f"{indent}  .{field} = {value} <{type(value)}>")
            setattr(self, field, value)

        def _append(field, obj_type, sexpr):
            match obj_type:
                case builtins.str:
                    value = sexpr
                case _:  # obj_type is a class
                    value = obj_type(sexpr, indent_level=indent_level + 1, parent=self)
            debug_print(f"{indent}  .{field} += {value} <{type(value)}>")
            getattr(self, field).append(value)

        do_pop = True
        for field, type_ in annotations.items():
            # lookup if the field is renamed to fullfill Python syntac
            py_field = field
            field = self.RENAMING.get(py_field, py_field)
            if py_field != field:
                debug_print(f"Field renamed {field} -> {py_field}")
            # pop cdr
            if do_pop:
                # get cdr head
                field_sexpr = cdr.pop(0) if cdr else None
            # lookup if the field has a default
            try:
                default_value = getattr(cls, py_field)
                has_default = True
            except AttributeError:
                has_default = False
            debug_print(
                f"{field}<{type_}> = {field_sexpr}" +
                " = '{default_value}'" if has_default else ' '
            )
            #
            match type_:
                case PositionalField():
                    value = self._to_python(type_.type, field_sexpr, indent_level)
                    _setattr(py_field, value)
                case _:
                    is_list = hasattr(type_, '__origin__') and type_.__origin__ == builtins.list
                    # if is_list:
                    #     debug_print('  is list')
                    if field_sexpr is None:  # cdr was poped
                        car = None
                        field_cdr = None
                    else:
                        car = car_value(field_sexpr)
                        field_cdr = S.cdr(field_sexpr)
                    if car == field:  # car match field
                        # debug_print(f'  field match {car}')
                        if is_list:
                            if not hasattr(self, py_field) or getattr(self, py_field) is None:
                                setattr(self, py_field, [])
                            obj_type = type_.__args__[0]
                            _append(py_field, obj_type, field_sexpr)
                            while cdr and car_value(cdr[0]) == field:
                                field_sexpr = cdr.pop(0)
                                _append(py_field, obj_type, field_sexpr)
                        else:
                            if isclass(type_) and issubclass(type_, SexprWrapper):
                                value = type_(field_sexpr, indent_level=indent_level + 1, parent=self)
                            else:
                                value = self._to_python(type_, field_cdr, indent_level)
                            _setattr(py_field, value)
                    else:  # field is not specified
                        if has_default:
                            # debug_print('  set default value')
                            if is_list:
                                _setattr(py_field, [])
                            else:
                                _setattr(py_field, default_value)
                            do_pop = False  # already done
                        else:
                            raise NameError(f"field {field} is missing for {self.__class__}")

    ##############################################

    @property
    def parent(self) -> object | None:
        return self._parent

    ##############################################

    def to_json(self) -> dict:
        cls = self.__class__
        annotations = annotationlib.get_annotations(cls)

        def _to_json(value):
            match value:
                case SexprWrapper():
                    return value.to_json()
                case list():
                    return [_to_json(_) for _ in value]
                case _:
                    return value

        d = {field: _to_json(getattr(self, field)) for field in annotations}
        d['__cls__'] = self.CAR
        return d
