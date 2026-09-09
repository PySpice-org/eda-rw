####################################################################################################
#
# EDA-RW — Python library to read/write EDA Sexpr file format
# Copyright (C) 2021 Fabrice SALVAIRE
# SPDX-License-Identifier: AGPL-3.0-or-later
#
####################################################################################################

"""Patch for sexpdata for KiCAD syntax.

Methods that require customizing the recursion or output string of `tosexp()` should be registered
with `@sexpdata.tosexp.register()`. Also the default handlers can be overridden by re-registration.
"""

####################################################################################################

import sexpdata as _sexpdata
from sexpdata import tosexp as _tosexp

####################################################################################################
#
# Customize float after "at"
#

_ROUND_2_SYMBOLS = ('at',)

@_tosexp.register(float)
def _(obj: float, **kwds: dict) -> str:
    if kwds['car_stack'][-1] in _ROUND_2_SYMBOLS:
        _ = round(obj, 2)
        return f'{_:.2f}'
    return str(obj)

####################################################################################################
#
# Customize the breaking of a KiCAD sexp
#

_BREAK_OPENER_SYMBOLS = (
    'effects',
    'fill',
    'name',
    'number',
    'pin',
    'property',
    'rectangle',
    'stroke',
    'symbol',
)

_BREAK_CLOSER_SYMBOLS = (
    'kicad_symbol_lib',
    'pin',
    'property',
    'rectangle',
    'symbol',
)

_BREAK_PREFIX_SYMBOLS = (
    'kicad_symbol_lib',
)

def _dont_break(car_stack: list, str_car: str) -> bool:
    return (str_car == 'effects' and car_stack[-1] in ('name', 'number'))

@_tosexp.register(_sexpdata.Delimiters)
def _(self, **kwds: dict) -> str:
    expr_separator = ' '
    exprs_indent = ''
    break_prefix_opener = ''
    break_prefix_closer = ''
    suffix_break = ''

    car = self.I[0]
    if isinstance(car, _sexpdata.Symbol):
        str_car = str(car)
        kwds.setdefault('car_stack', [])  # ty: ignore[no-matching-overload]
        if str_car in _BREAK_OPENER_SYMBOLS and not _dont_break(kwds['car_stack'], str_car):  # ty: ignore[invalid-argument-type]
            exprs_indent = '  '
            break_prefix_opener = '\n' + exprs_indent
        if str_car in _BREAK_CLOSER_SYMBOLS:
            break_prefix_closer = '\n' + exprs_indent
        kwds['car_stack'].append(str_car)  # ty: ignore[unresolved-attribute]
        if str_car in _BREAK_PREFIX_SYMBOLS:
            suffix_break = '\n'

    exprs = expr_separator.join(_tosexp(x, **kwds) for x in self.I)
    indented_exprs = '\n'.join(exprs_indent + line.rstrip() for line in exprs.splitlines(True))
    indented_exprs = indented_exprs[len(exprs_indent):]

    if kwds.get('car_stack'):
        kwds['car_stack'].pop()  # ty: ignore[no-matching-overload]

    return (
        break_prefix_opener + self.__class__.opener +
        indented_exprs +
        break_prefix_closer + self.__class__.closer + suffix_break
    )
