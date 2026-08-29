####################################################################################################
#
# KiCad-RW — Python library to read/write KiCad Sexpr file format
# Copyright (C) 2021 Fabrice SALVAIRE
# SPDX-License-Identifier: AGPL-3.0-or-later
#
####################################################################################################

__all__ = [
    'SymbolLibrary',
]

####################################################################################################

from enum import Enum, IntEnum, auto
from typing import Any

from . import Symbol, dumps
# from . import SexpSymbols as Sym
# pylint: disable=no-name-in-module
from .SexpSymbols import (
    AT,
    BACKGROUND,
    COLOR,
    DEFAULT,
    EFFECTS,
    END,
    EXTENDS,
    FILL,
    FONT,
    GENERATOR,
    HIDE,
    ID,
    IN_BOM,
    ITALIC,
    JUSTIFY,
    KICAD_SYMBOL_LIB,
    LENGTH,
    LINE,
    NAME,
    NO,
    NUMBER,
    ON_BOARD,
    PIN,
    PROPERTY,
    RECTANGLE,
    SIZE,
    START,
    STROKE,
    SYMBOL,
    TYPE,
    VERSION,
    WIDTH,
    YES,
)
# pylint: enable=no-name-in-module

####################################################################################################

def ensure_int_float(_: Any) -> float:
    if isinstance(_, (int, float)):
        return _
    return float(_)

def ensure_int_float_x(_: Any, n: int) -> list[float]:
    return [ensure_int_float(_) for _ in _[:n]]

def ensure_int_float_2(_: Any) -> list[float, float]:
    return ensure_int_float_x(_, 2)

def ensure_int_float_3(_: Any) -> list[float, float]:
    return ensure_int_float_x(_, 3)

def ensure_int_float_4(_: Any) -> list[float, float]:
    return ensure_int_float_x(_, 4)

####################################################################################################

class JustifyStyle(IntEnum):
    ANY = 0
    LEFT = 1 << 1
    RIGHT = 1 << 2
    BOTTOM = 1 << 3
    TOP = 1 << 4

class Direction(IntEnum):
    LEFT = 180
    RIGHT = 0
    BOTTOM = 270
    TOP = 90

####################################################################################################

class FontMixin:

    ##############################################

    def __init__(self,
                 font_size: tuple[float, float],
                 italic: bool = False,
                 justify: JustifyStyle = JustifyStyle.ANY,
                 ) -> None:
        self._font_size = ensure_int_float_2(font_size)
        self._italic = bool(italic)
        self._justify = int(justify)

    ##############################################

    def __to_lisp_as__(self) -> list:
        font = [FONT, (SIZE, *self._font_size)]
        if self._italic:
            font.append(ITALIC)
        effects = [font]
        justify = [
            Symbol(str(_).split('.')[1].lower())
            for _ in JustifyStyle
            if _ & self._justify
        ]
        if justify:
            effects.append([JUSTIFY] + justify)
        return (EFFECTS, *effects)

####################################################################################################

class Property(FontMixin):

    ##############################################

    def __init__(self,
                 name: str,
                 value: str,
                 font_size: tuple[float, float],
                 id_: int,
                 at: tuple[float, float] = (0, 0),
                 italic: bool = False,
                 justify: JustifyStyle = JustifyStyle.ANY,
                 hide: bool = False,
                 ) -> None:
        FontMixin.__init__(
            self,
            font_size=font_size,
            italic=italic,
            justify=justify,
        )
        self._id = int(id_)
        self._name = str(name)
        self._value = str(value)
        self._at = ensure_int_float_2(at)
        self._hide = bool(hide)

    ##############################################

    def __to_lisp_as__(self) -> list:
        effects = list(FontMixin.__to_lisp_as__(self))
        if self._hide:
            effects.append(HIDE)
        sexp = [
            PROPERTY, self._name, self._value,
            (ID, self._id),
            (AT, *self._at, 0),
            effects,
        ]
        return sexp

####################################################################################################

class RectangularShape:

    ##############################################

    def __init__(self,
                 name: str,
                 start: tuple[float, float],
                 end: tuple[float, float],
                 stroke_width: float = 0.254,
                 color: list[float, float, float, float] = (0, 0, 0, 0),
                 ) -> None:
        self._name = str(name)
        self._stroke_width = float(stroke_width)
        self._start = ensure_int_float_2(start)
        self._end = ensure_int_float_2(end)
        self._color = ensure_int_float_4(color)

    ##############################################

    def __to_lisp_as__(self) -> list:
        return (
            SYMBOL, self._name,
            (RECTANGLE, (START, *self._start), (END, *self._end),
             (STROKE, (WIDTH, self._stroke_width), (TYPE, DEFAULT), (COLOR, *self._color)),
             (FILL, (TYPE, BACKGROUND)),
             )
        )

####################################################################################################

class Pin(FontMixin):

    ##############################################

    def __init__(self,
                 name: str,
                 number: int,
                 type_: str,
                 at: tuple[float, float],
                 angle: int,
                 length: float,
                 font_size: tuple[float, float],
                 hide: False,
                 ) -> None:
        FontMixin.__init__(
            self,
            font_size=font_size,
            # italic=italic,
            # justify=justify,
        )
        self._name = str(name)
        self._number = int(number)
        self._type = str(type_)
        self._at = ensure_int_float_2(at)
        self._angle = int(angle)
        self._length = float(length)
        self._hide = bool(hide)

    ##############################################

    def __to_lisp_as__(self) -> list:
        sexp = [
            PIN,
            Symbol(self._type),
            LINE,
            (AT, *self._at, self._angle),
            (LENGTH, self._length),
        ]
        if self._hide:
            sexp.append(HIDE)
        sexp += [
            (NAME, self._name, FontMixin.__to_lisp_as__(self)),
            (NUMBER, str(self._number), FontMixin.__to_lisp_as__(self)),
        ]
        return sexp

####################################################################################################

class PropertyMixin:

    ##############################################

    def __init__(self) -> None:
        self._properties = []

    ##############################################

    def add_property(self, *args: list, **kwargs: dict) -> Property:
        _ = Property(*args, **kwargs, id_=len(self._properties))
        self._properties.append(_)
        return _

####################################################################################################

class Part(PropertyMixin):

    ##############################################

    def __init__(self,
                 name: str,
                 in_bom: bool = True,
                 in_board: bool = True,
                 ) -> None:
        PropertyMixin.__init__(self)
        self._name = str(name)
        self._shapes = []
        self._pins = []
        self._in_bom = bool(in_bom)
        self._in_board = bool(in_board)

    ##############################################

    def add_rectangle(self, *args: list, **kwargs: dict) -> RectangularShape:
        name = f'{self._name}_0_{len(self._shapes) +1}'
        _ = RectangularShape(*args, **kwargs, name=name)
        self._shapes.append(_)
        return _

    ##############################################

    def add_pin(self, *args: list, **kwargs: dict) -> Pin:
        _ = Pin(*args, **kwargs)
        self._pins.append(_)
        return _

    ##############################################

    def __to_lisp_as__(self) -> list:
        return [
            SYMBOL,
            self._name,
            (IN_BOM, YES if self._in_bom else NO),
            (ON_BOARD, YES if self._in_board else NO),
            *self._properties,
            *self._shapes,
            [SYMBOL, f'{self._name}_1_1', *self._pins]
        ]

####################################################################################################

class ExtendedPart(PropertyMixin):

    ##############################################

    def __init__(self,
                 name: str,
                 base_name: str,
                 ) -> None:
        PropertyMixin.__init__(self)
        self._name = str(name)
        self._base_name = str(base_name)

    ##############################################

    def __to_lisp_as__(self) -> list:
        return [SYMBOL, self._name, (EXTENDS, self._base_name), *self._properties]

####################################################################################################

class SymbolLibrary:

    ##############################################

    def __init__(self,
                 version: str,
                 generator: str = 'kicad_symbol_editor',
                 ) -> None:
        self._version = str(version)
        self._generator = str(generator)
        self._parts = []

    ##############################################

    def add_part(self, *args: list, **kwargs: dict) -> Part:
        _ = Part(*args, **kwargs)
        self._parts.append(_)
        return _

    def add_extended_part(self, *args: list, **kwargs: dict) -> ExtendedPart:
        _ = ExtendedPart(*args, **kwargs)
        self._parts.append(_)
        return _

    ##############################################

    def __to_lisp_as__(self) -> list:
        return [
            KICAD_SYMBOL_LIB,
            (VERSION, Symbol(self._version)),
            (GENERATOR, Symbol(self._generator)),
            *self._parts,
        ]

    ##############################################

    def dumps(self) -> str:
        return dumps(self)
