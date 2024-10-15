####################################################################################################
#
# KiCad-RW — Python library to read/write KiCad Sexpr file format
# Copyright (C) 2021 Fabrice Salvaire
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
####################################################################################################

"""Patch for sexpdata
"""

####################################################################################################

import sexpdata as _sexpdata
from sexpdata import tosexp as _tosexp

# for __init__.py
from sexpdata import loads, dumps, Symbol

####################################################################################################

_ROUND_2_SYMBOLS = ('at',)

@_tosexp.register(float)
def _(obj: float, **kwds: dict) -> str:
    if kwds['car_stack'][-1] in _ROUND_2_SYMBOLS:
        _ = round(obj, 2)
        return f'{_:.2f}'
    return str(obj)

####################################################################################################

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
        kwds.setdefault('car_stack', [])
        if str_car in _BREAK_OPENER_SYMBOLS and not _dont_break(kwds['car_stack'], str_car):
            exprs_indent = '  '
            break_prefix_opener = '\n' + exprs_indent
        if str_car in _BREAK_CLOSER_SYMBOLS:
            break_prefix_closer = '\n' + exprs_indent
        kwds['car_stack'].append(str_car)
        if str_car in _BREAK_PREFIX_SYMBOLS:
            suffix_break = '\n'

    exprs = expr_separator.join(_tosexp(x, **kwds) for x in self.I)
    indented_exprs = '\n'.join(exprs_indent + line.rstrip() for line in exprs.splitlines(True))
    indented_exprs = indented_exprs[len(exprs_indent):]

    if kwds.get('car_stack', None):
        kwds['car_stack'].pop()

    return (
        break_prefix_opener + self.__class__.opener +
        indented_exprs +
        break_prefix_closer + self.__class__.closer + suffix_break
    )
