####################################################################################################
#
# KiCad-RW — Python library to read/write KiCad Sexpr file format
# Copyright (C) 2021 Fabrice SALVAIRE
# SPDX-License-Identifier: AGPL-3.0-or-later
#
####################################################################################################

__all__ = [
    'Sexpression',
    'car',
    'car_value',
    'cdr',
]

####################################################################################################

import sexpdata
from sexpdata import Symbol, car, cdr

####################################################################################################

def get_value(_: Symbol) -> str:
    if isinstance(_, Symbol):
        return str(_)
    else:
        # print(f">>> {type(_)} {_}")
        return _.value()   # Fixme: type ???

def car_value(_: tuple | list) -> str:
    return get_value(car(_))

####################################################################################################

class Sexpression:

    ##############################################

    @classmethod
    def to_dict(cls, sexpr: tuple | list) -> tuple | list:
        """Convert a S-expression to JSON"""
        if isinstance(car(sexpr), Symbol):
            d = {'_': []}
            for item in cdr(sexpr):
                if isinstance(item, Symbol):
                    d['_'].append(get_value(item))
                elif isinstance(item, list):
                    key, value = cls.to_dict(item)
                    # some keys can appear more than one time...
                    while key in d:
                        key += '*'
                    d[key] = value
                if isinstance(item, (int, float, str)):
                    d['_'].append(item)
            if d['_']:
                if len(d.keys()) == 1:
                    d = d['_']
                    if len(d) == 1:
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
        """Fix key*... as a dict"""
        new_dict = {}
        while key in adict:
            d = adict[key]
            del adict[key]
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
            d = adict[key]
            del adict[key]
            new_list.append(d)
            key += '*'
        if new_list:
            adict[new_key] = new_list

    ##############################################

    @classmethod
    def sattr(cls, d: dict | None) -> str:
        if d is not None:
            return d['_'][0]
        else:
            # Fixme: schema expects a str
            return None  # ty: ignore[invalid-return-type]

    ##############################################

    @classmethod
    def load(cls, path: str) -> list:
        with open(path) as fh:
            _ = sexpdata.load(fh)
        return _
