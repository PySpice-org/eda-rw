####################################################################################################
#
# KiCad-RW — Python library to read/write KiCad Sexpr file format
# Copyright (C) 2021 Fabrice SALVAIRE
# SPDX-License-Identifier: AGPL-3.0-or-later
#
####################################################################################################

from pathlib import Path

from KiCadRW.sexp.schema import KiCadSchema
from KiCadRW.log import setup_logging

####################################################################################################

logger = setup_logging()

####################################################################################################

# schema_path = Path(
#     'kicad-examples',
#     'capacitive-half-wave-rectification-pre-zener',
#     'capacitive-half-wave-rectification-pre-zener.kicad_sch'
# )

# schema_path = Path(
#     'kicad-examples',
#     'single-sheet',
#     'single.kicad_sch'
# )

schema_path = Path('/home/fabrice/__projects__/pyspice/kicad-schema/charge-pump/charge-pump.kicad_sch')

kicad_schema = KiCadSchema(schema_path)
kicad_schema.dump_netlist()
