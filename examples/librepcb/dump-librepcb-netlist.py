####################################################################################################
#
# EDA-RW — Python library to read/write EDA Sexpr file format
# Copyright (C) 2021 Fabrice SALVAIRE
# SPDX-License-Identifier: AGPL-3.0-or-later
#
####################################################################################################

from pathlib import Path

from edarw.eda.librepcb.circuit import Circuit
from edarw.log import setup_logging

####################################################################################################

logger = setup_logging()

####################################################################################################

circuit_path = Path('../../librepcb-examples/calidou/circuit/circuit.lp')

circuit = Circuit.load(circuit_path)

