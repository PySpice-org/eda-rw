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
from collections.abc import Iterable
from typing import Self

####################################################################################################

class TextBuffer:
    """Build indented text output one line at a time."""

    # Note: object.__str__() call object.__repr__()

    ##############################################

    def __init__(self, indent: int = 4) -> None:
        """Initialize the buffer with a given indentation width."""
        self._lines: list[str] = []
        self._indentation = ' ' * indent
        self._indent_level = 0

    ##############################################

    def __len__(self) -> int:
        """Return the number of lines currently stored in the buffer."""
        return len(self._lines)

    ##############################################

    def indent(self) -> None:
        """Increase the current indentation level by one."""
        self._indent_level += 1

    def dedent(self) -> None:
        """Decrease the current indentation level by one when possible."""
        if self._indent_level >= 1:
            self._indent_level -= 1

    ##############################################

    def _append_line(self, line: str | object | None) -> None:
        """Append a single non-empty line at the current indentation level."""
        if line is not None:
            _ = str(line)
            if _:
                _ = self._indentation * self._indent_level + _
                self._lines.append(_)

    ##############################################

    def __iadd__(self, obj: str | object | Iterable | None) -> Self:
        """Append one line or a sequence of lines to the buffer using the `__str__` protocol."""
        match obj:
            case str():
                self._append_line(obj)
            case Iterable():  # str is an Iterable
                for _ in obj:
                    self._append_line(_)
            case _:
                self._append_line(obj)
        return self

    ##############################################

    def new_line(self, count: int = 1) -> None:
        """Insert one or more blank lines into the buffer."""
        for _ in range(count):
            self._lines.append('')

    ##############################################

    def __str__(self) -> str:
        """Return the buffer contents as a single text string."""
        return os.linesep.join(self._lines) + os.linesep
