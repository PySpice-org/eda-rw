####################################################################################################
#
# KiCad-RW — Python library to read/write KiCad Sexpr file format
# Copyright (C) 2021 Fabrice SALVAIRE
# SPDX-License-Identifier: AGPL-3.0-or-later
#
####################################################################################################

from pathlib import Path

from kicadrw.librepcb.circuit import Circuit
from kicadrw.log import setup_logging

####################################################################################################

logger = setup_logging()

####################################################################################################

circuit_path = Path('../librepcb-examples/calidou/circuit/circuit.lp')

circuit = Circuit(circuit_path)
# kicad_schema.dump_circuit()
