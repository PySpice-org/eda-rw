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
from sexpdata import car, cdr, Symbol

####################################################################################################

def get_value(_):
    if isinstance(_, Symbol):
        return str(_)
    else:
        return _.value()

def car_value(_):
    return get_value(car(_))

####################################################################################################

class Sexpression:

    ##############################################

    @classmethod
    def to_dict(cls, sexpr):
        """Convert a S-expression to JSON"""
        if isinstance(car(sexpr), sexpdata.Symbol):
            d = {'_': []}
            for item in cdr(sexpr):
                if isinstance(item, sexpdata.Symbol):
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
    def fix_key_as_dict(cls, adict, key, new_key):
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
    def fix_key_as_list(cls, adict, key, new_key):
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
    def sattr(cls, d: dict):
        if d is not None:
            return d['_'][0]
        else:
            return None

    ##############################################

    @classmethod
    def load(cls, path: str):
        with open(path) as fh:
            _ = sexpdata.load(fh)
        return _
