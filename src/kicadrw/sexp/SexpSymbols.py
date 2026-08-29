####################################################################################################
#
# KiCad-RW — Python library to read/write KiCad Sexpr file format
# Copyright (C) 2021 Fabrice SALVAIRE
# SPDX-License-Identifier: AGPL-3.0-or-later
#
####################################################################################################

import sys as _sys
from sexpdata import Symbol as _Symbol

####################################################################################################

_module = _sys.modules[__name__]

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
