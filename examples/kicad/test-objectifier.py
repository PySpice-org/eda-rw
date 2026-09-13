####################################################################################################
#
# EDA-RW — Python library to read/write EDA Sexpr file format
# Copyright (C) 2021 Fabrice SALVAIRE
# SPDX-License-Identifier: AGPL-3.0-or-later
#
####################################################################################################

from pathlib import Path
from pprint import pprint

from edarw.log import setup_logging
from edarw.objectifier import Objectifier, SchemaNode

####################################################################################################

logger = setup_logging()

####################################################################################################

examples_path = Path('kicad-examples')
path = ('capacitive-half-wave-rectification-pre-zener', 'capacitive-half-wave-rectification-pre-zener.kicad_sch')
# path = ('open-syringe-pump', 'indus', 'opensyringepump_indus.kicad_sch')
# path = ('electrolab-cta-control-board', 'CTA_control_board.kicad_sch')
# path = ('electrolab-cta-control-board', 'CTA_control_board.kicad_sch')
# path = ('symbols', 'Infineon_IGBT_Driver.kicad_sym')
schema_path = examples_path.joinpath(*path)

objectifier = Objectifier(schema_path)

# Dump sexp structure
# objectifier.dump()

# Dump sexp paths
# objectifier.get_paths()

# Dump nodes
objectifier.get_schema()
pprint(SchemaNode.NODES)

if schema_path.suffix == '.kicad_sch':
    root = objectifier.root
    print(root.xpath('/kicad_sch/version'))
    print('---')
    for node in root.xpath('/kicad_sch/lib_symbols/symbol'):
        print(f"{node.path_str}: {node.first_child}")
    print('---')
    for node in root.xpath('/kicad_sch/symbol/lib_id'):
        print(f"{node.path_str}: {node.first_child}")
    print('---')
    for node in root.xpath('/kicad_sch/symbol'):
        print(f"{node.path_str}: {node.first_child}")
        for _ in node.xpath('property'):
            print(f"    {_.path_str}: {_.childs[:2]}")
