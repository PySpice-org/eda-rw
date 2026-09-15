####################################################################################################
#
# PySpice - A Spice Package for Python
# Copyright (C) 2020 Fabrice Salvaire
# SPDX-License-Identifier: AGPL-3.0-or-later
#
####################################################################################################

__all__ = ['main']

####################################################################################################

import argparse
from pathlib import Path

from rich import print
from rich.console import Console
from rich.syntax import Syntax

from edarw.log import setup_logging
from edarw.eda.librepcb.project import Project

####################################################################################################

logger = setup_logging()

console = Console()

####################################################################################################

def main() -> None:
    parser = argparse.ArgumentParser(description='Generate LibrePcb Python module')

    parser.add_argument(
        'input',
        # metavar='input',
        help='.lp file',
    )

    parser.add_argument(
        '-o',
        '--output',
        default=None,
        help='Output file',
    )

    args = parser.parse_args()

    input_path = Path(args.input)
    cls = Project.guess_loader(input_path)
    print(f"File [blue]{input_path}[/] is a {cls}")
    if cls is Project:
        pass
    else:
        obj = cls.load(input_path, project=None)
        sexpr = obj.to_sexpr()
        if args.output:
            path = Path(args.output)
            print(f"Write {path}")
            path.write_text(sexpr)
        else:
            # _ = Syntax(sexpr, 'lisp')
            # print(_)
            print(sexpr)
