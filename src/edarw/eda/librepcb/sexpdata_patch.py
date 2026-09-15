####################################################################################################
#
# EDA-RW — Python library to read/write EDA Sexpr file format
# Copyright (C) 2021 Fabrice SALVAIRE
# SPDX-License-Identifier: AGPL-3.0-or-later
#
####################################################################################################

"""Patch for sexpdata for LibrePcb syntax.

Methods that require customizing the recursion or output string of `tosexp()` should be registered
with `@sexpdata.tosexp.register()`. Also the default handlers can be overridden by re-registration.
"""

####################################################################################################

import logging

import sexpdata as S
from sexpdata import tosexp as _tosexp

####################################################################################################

_module_logger = logging.getLogger(__name__)

# _module_logger.info("Patch sexpdata for LibrePCB")
print("Patch sexpdata for LibrePCB")

####################################################################################################
#
# Customize float after "at"
#

# _ROUND_2_SYMBOLS = ('at',)

# @_tosexp.register(float)
# def _(obj: float, **kwds: dict) -> str:
#     if kwds['car_stack'][-1] in _ROUND_2_SYMBOLS:
#         _ = round(obj, 2)
#         return f'{_:.2f}'
#     return str(obj)

####################################################################################################
#
# Customize the breaking of a KiCAD sexp
#

_BREAK_OPENER_SYMBOLS = (
    'librepcb_circuit',
)

_BREAK_CLOSER_SYMBOLS = (
)

_BREAK_PREFIX_SYMBOLS = (
)

def _dont_break(car_stack: list, str_car: str) -> bool:
    return (str_car == 'effects' and car_stack[-1] in ('name', 'number'))

#@_tosexp.register(S.Delimiters)
def d_(self, **kwds: dict) -> str:
    car_stack = kwds.setdefault('car_stack', [])  # ty: ignore[no-matching-overload]

    expr_separator = ' '
    INDENTATION = ' ' * 2
    exprs_indent = INDENTATION * len(car_stack)
    break_prefix_opener = ''
    break_prefix_closer = ''
    suffix_break = ''
    car_break = ''

    car = self.I[0]
    if isinstance(car, S.Symbol):
        str_car = str(car)
        cdr = self.I[1:]

        #  and not _dont_break(car_stack, str_car)
        if str_car in _BREAK_OPENER_SYMBOLS:  # ty: ignore[invalid-argument-type]
            # exprs_indent = '  '
            # break_prefix_opener = '\n' + exprs_indent
            car_break = '\n'
        if str_car in _BREAK_CLOSER_SYMBOLS:
            break_prefix_closer = '\n' + exprs_indent
        if str_car in _BREAK_PREFIX_SYMBOLS:
            suffix_break = '\n'

        car_stack.append(str_car)  # ty: ignore[unresolved-attribute]

        exprs = [_tosexp(x, **kwds) for x in cdr]
        exprs = [exprs_indent + INDENTATION + _ for _ in exprs]
        exprs = '\n'.join(exprs)

        # exprs = expr_separator.join(_tosexp(x, **kwds) for x in cdr)
        # indented_exprs = '\n'.join(exprs_indent + line.rstrip() for line in exprs.splitlines(True))
        # indented_exprs = indented_exprs[len(exprs_indent):]

        sexpr = (
            exprs_indent + self.__class__.opener + str_car + '\n' +
            # indented_exprs +
            exprs + '\n' +
            exprs_indent + self.__class__.closer + '\n'
        )
    else:
        exprs = expr_separator.join(_tosexp(x, **kwds) for x in self.I)
        # indented_exprs = '\n'.join(exprs_indent + line.rstrip() for line in exprs.splitlines(True))
        # indented_exprs = indented_exprs[len(exprs_indent):]

        # sexpr = (
        #     break_prefix_opener + self.__class__.opener +
        #     indented_exprs +
        #     break_prefix_closer + self.__class__.closer + suffix_break
        # )

        sexpr = (
            self.__class__.opener +
            exprs +
            self.__class__.closer
        )

    if kwds.get('car_stack'):
        car_stack.pop()  # ty: ignore[no-matching-overload]

    return sexpr

####################################################################################################

DONT_BREAK_OVERLOADS = [_tosexp.dispatch(c) for c in (object, S.Iterable, S.Mapping, tuple, S.Delimiters)]

@_tosexp.register(S.Delimiters)
def _(self, **kwds):
    # Don't break up expressions produced by certain overloads of tosexp
    dont_break = all(_tosexp.dispatch(type(x)) not in DONT_BREAK_OVERLOADS for x in self.I)

    if "pretty_print" in kwds and kwds["pretty_print"] and not dont_break:
        expr_separator = "\n"
        exprs_indent = kwds["indent_as"] if "indent_as" in kwds else "  "
        exprs_separator = "\n"
    else:
        expr_separator = " "
        exprs_indent = ""
        exprs_separator = ""

    exprs = expr_separator.join(_tosexp(x, **kwds) for x in self.I)
    indented_exprs = "".join(exprs_indent + line for line in exprs.splitlines(True))

    return (
        self.__class__.opener +
        exprs_separator +
        indented_exprs +
        exprs_separator +
        self.__class__.closer
    )
