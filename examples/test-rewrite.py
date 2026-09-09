####################################################################################################
#
# EDA-RW — Python library to read/write EDA Sexpr file format
# Copyright (C) 2021 Fabrice SALVAIRE
# SPDX-License-Identifier: AGPL-3.0-or-later
#
####################################################################################################

from pathlib import Path
from pprint import pprint

# https://sexpdata.readthedocs.io/en/latest/
# https://github.com/jd-boyd/sexpdata
import sexpdata

####################################################################################################

schema_path = Path(
    'kicad-examples',
    'capacitive-half-wave-rectification-pre-zener',
    'capacitive-half-wave-rectification-pre-zener.kicad_sch'
)

####################################################################################################
#
# Lisp
#
# tuple = ( foo   1 'string' ... )
#       = ( car | cdr            )
#
#  car(tuple) = foo
#  cdr(tuple) = (1 'string' ... )
#
#  foo is a Symbol and not a string, usually a function in Lisp, e.g.
#
#    (sum 1 2 3 ...)
#
# Types
#  - Symbol('...')
#  - str
#  - int
#  - float
#
# Sexpr
#   sexpr   = [symbol element ...]
#   element = sexpr
#           | str
#           | int
#           | float
#
####################################################################################################

print(f"Load {schema_path}")
with open(schema_path) as fh:
    sexpr = sexpdata.load(fh)

pprint(sexpr)

new_schema_path = schema_path.name
with open(new_schema_path, 'w') as fh:
    # str_as ('symbol' or 'string') – How string should be interpreted. Default is 'string'.
    # tuple_as ('list' or 'array') – How tuple should be interpreted. Default is 'list'.
    # true_as (str) – How True should be interpreted. Default is 't'
    # false_as (str) – How False should be interpreted. Default is '()'
    # none_as (str) – How None should be interpreted. Default is '()'
    sexpdata.dump(
        sexpr, fh,
    )
    print(f'Write {new_schema_path}')
