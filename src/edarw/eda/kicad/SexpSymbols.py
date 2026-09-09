####################################################################################################
#
# EDA-RW — Python library to read/write EDA Sexpr file format
# Copyright (C) 2021 Fabrice SALVAIRE
# SPDX-License-Identifier: AGPL-3.0-or-later
#
####################################################################################################

# ruff: ignore[undefined-export]

__all__ = [
    'AT',
    'BACKGROUND',
    'BOTTOM',
    'COLOR',
    'DEFAULT',
    'EFFECTS',
    'END',
    'EXTENDS',
    'FILL',
    'FONT',
    'GENERATOR',
    'HIDE',
    'ID',
    'IN_BOM',
    'ITALIC',
    'JUSTIFY',
    'KICAD_SYMBOL_LIB',
    'LEFT',
    'LENGTH',
    'LINE',
    'NAME',
    'NO',
    'NUMBER',
    'ON_BOARD',
    'PIN',
    'PROPERTY',
    'RECTANGLE',
    'SIZE',
    'START',
    'STROKE',
    'SYMBOL',
    'TOP',
    'TYPE',
    'VERSION',
    'WIDTH',
    'YES',
]

####################################################################################################

import sys as _sys

from sexpdata import Symbol as _Symbol

####################################################################################################

_module = _sys.modules[__name__]

# Define these symbols in the current module
for _name in (
    'at',

    'background',

    'bottom',

    'color',

    'default',

    'effects',
    'end',
    'extends',

    'fill',
    'font',

    'generator',

    'hide',

    'id',
    'in_bom',
    'italic',

    'justify',

    'kicad_symbol_lib',

    'left',
    'length',
    'line',

    'name',
    'no',
    'number',

    'on_board',

    'pin',
    'property',

    'rectangle',

    'size',
    'start',
    'stroke',
    'symbol',

    'top',
    'type',

    'version',

    'width',

    'yes',
):
    setattr(_module, _name.upper(), _Symbol(_name))
