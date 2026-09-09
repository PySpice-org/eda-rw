####################################################################################################
#
# EDA-RW — Python library to read/write EDA Sexpr file format
# Copyright (C) 2021 Fabrice SALVAIRE
# SPDX-License-Identifier: AGPL-3.0-or-later
#
####################################################################################################

"""

A sexpr is `(car . cdr)`

https://en.wikipedia.org/wiki/S-expression

"""

####################################################################################################

__all__ = [
    'Sexpression',
    'car',
    'car_value',
    'cdr',
]

####################################################################################################

import sexpdata
# from rich import print
from sexpdata import Symbol, car, cdr

####################################################################################################

def get_value(_: Symbol) -> str:
    """Return `component` for `Symbol('component')`"""
    if isinstance(_, Symbol):
        return str(_)
    else:
        # print(f">>> {type(_)} {_}")
        return _.value()   # Fixme: type ???

def car_value(_: tuple | list) -> str:
    """Return `component` for `(Symbol('component' . cdr))`"""
    return get_value(car(_))

####################################################################################################

class Sexpression:

    ##############################################

    @classmethod
    def to_dict(cls, sexpr: tuple | list) -> tuple | list:
        """Convert a S-expression to JSON

        Return (car, dict)
        """
        # print(sexpr)
        if isinstance(car(sexpr), Symbol):
            # key _ collects the values which are not a sexpr
            d = {'_': []}

            def append_(x):
                d['_'].append(x)  # ty: ignore[invalid-argument-type]

            for item in cdr(sexpr):
                match item:
                    case Symbol():
                        append_(get_value(item))
                    case int() | float() | str():
                        append_(item)
                    case list():
                        key, value = cls.to_dict(item)
                        # some keys can appear more than one time...
                        while key in d:
                            key += '*'
                        d[key] = value
                        # if key in d:
                        #     list_key = f'{key}s'
                        #     if list_key not in d:
                        #         d[list_key] = [d.pop(key)]
                        #     d[list_key].append(value)
                        # else:
                        #     d[key] = value
            # simplify
            if d['_']:
                if len(d.keys()) == 1:  # keys == ('_',)
                    d = d['_']
                    if len(d) == 1:  # singleton
                        d = d[0]
            else:
                # Fixme: could use d.get('_', []) ???
                del d['_']
            return car_value(sexpr), d
        else:
            return sexpr

    ##############################################

    @classmethod
    def fix_key_as_dict(cls, adict: dict, key: str, new_key: str) -> None:
        """Fix key*... as a dict

        e.g. KiCAD
        ```
        [
            Symbol('property'),
            'Reference',
            'C',
            [Symbol('at'), 0.635, 2.54, 0],
            [Symbol('show_name'), Symbol('no')],
            [Symbol('do_not_autoplace'), Symbol('no')],
            [Symbol('effects'), [Symbol('font'), [Symbol('size'), 1.27, 1.27]], [Symbol('justify'), Symbol('left')]]
        ],

        'property': {
             '_': ['Reference', 'C'],
             'at': [0.635, 2.54, 0],
             'show_name': 'no',
             'do_not_autoplace': 'no',
             'effects': {'font': {'size': [1.27, 1.27]}, 'justify': 'left'}
             },
        ```
        """
        # print(key, adict)
        new_dict = {}
        while key in adict:
            d = adict.pop(key)
            key2 = d['_'][0]
            d['_'] = d['_'][1:]
            new_dict[key2] = d
            key += '*'
        if new_dict:
            adict[new_key] = new_dict

    ##############################################

    @classmethod
    def fix_key_as_list(cls, adict: dict, key: str, new_key: str) -> None:
        """Fix key*... as a list"""
        new_list = []
        while key in adict:
            new_list.append(adict.pop(key))
            key += '*'
        if new_list:
            adict[new_key] = new_list

    ##############################################

    @classmethod
    def sattr(cls, d: dict | str | None) -> str:
        match d:
            case dict():
                return d['_'][0]
            case '' | None:
                # return None # Fixme: '' vs None
                return ''
            case _:
                raise NotImplementedError

    ##############################################

    @classmethod
    def load(cls, path: str) -> list:
        with open(path) as fh:
            _ = sexpdata.load(fh)
        return _
