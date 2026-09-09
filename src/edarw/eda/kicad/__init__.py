####################################################################################################
#
# EDA-RW — Python library to read/write EDA Sexpr file format
# Copyright (C) 2021 Fabrice SALVAIRE
# SPDX-License-Identifier: AGPL-3.0-or-later
#
####################################################################################################

# Patch sexpdata
from . import patch as _patch  # ruff: ignore[unused-import]
from .SexpSymbols import *  # ruff: ignore[undefined-local-with-import-star]
