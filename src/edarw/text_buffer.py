####################################################################################################
#
# EDA-RW — Python library to read/write EDA Sexpr file format
# Copyright (C) 2026 Fabrice SALVAIRE
# SPDX-License-Identifier: AGPL-3.0-or-later
#
####################################################################################################

__all__ = ['TextBuffer']

####################################################################################################

import os
from typing import Self

####################################################################################################

class TextBuffer:

    # Note: object.__str__() call object.__repr__()

    ##############################################

    def __init__(self, indent: int = 4) -> None:
        self._lines: list[str] = []
        self._indentation = ' ' * indent
        self._indent_level = 0

    ##############################################

    def indent(self) -> None:
        self._indent_level += 1

    def dedent(self) -> None:
        if self._indent_level >= 1:
            self._indent_level -= 1

    ##############################################

    def _append_line(self, line: str | object | None) -> None:
        if line is not None:
            _ = str(line)
            if _:
                _ = self._indentation * self._indent_level + _
                self._lines.append(_)

    ##############################################

    def __iadd__(self, obj: tuple | list | str | object | None) -> Self:
        match obj:
            case tuple() | list():  # str is an Iterable
                for _ in obj:
                    self._append_line(_)
            case _:
                self._append_line(obj)
        return self

    ##############################################

    def new_line(self, count: int = 1) -> None:
        for _ in range(count + 1):
            self._lines.append('')

    ##############################################

    def __str__(self) -> str:
        return os.linesep.join(self._lines)
