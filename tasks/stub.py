####################################################################################################
#
# EDA-RW — Python library to read/write EDA Sexpr file format
# Copyright (C) 2026 Fabrice SALVAIRE
# SPDX-License-Identifier: AGPL-3.0-or-later
#
####################################################################################################

# - [PEP 484 – Type Hints — Stub Files | peps.python.org](https://peps.python.org/pep-0484/#stub-files)
# - [Automatic stub generation (stubgen) - mypy 2.3.1 documentation](https://mypy.readthedocs.io/en/stable/stubgen.html)
# ty doesn't merge pi and .pyi

# find src -name "*pyi_" -exec mv {} __TRASH__ \;

# for TYPE_CHECKING
# def signal_def(~ERROR~ 'property' object has no attribute 'Signal'): ...
# def component_def(~ERROR~ name 'component' is not defined): ...
# def load(~ERROR~ name 'Project' is not defined): ...
# def project(~ERROR~ name 'Project' is not defined): ...
# def load(~ERROR~ name 'Project' is not defined): ...
# def load(~ERROR~ name 'Self' is not defined): ...

####################################################################################################

import annotationlib
import builtins
import inspect
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Any, Literal, Self

from invoke import task, Context
from rich import print

from edarw.eda.librepcb import component, project, schematic, symbol
from edarw.sexpr import PositionalField, SexprWrapper
from edarw.text_buffer import TextBuffer

####################################################################################################

@task
def generate(ctx: Context) -> None:
    root = Path('src')

    for cls in SexprWrapper._CLASSES:
        module_path = root / cls.__module__.replace('.', '/')
        pyi_path = module_path.parent / (module_path.name + '.pyi_')

        buffer = TextBuffer()
        #! buffer.new_line(2)

        buffer += f"class {cls.__name__}(SexprWrapper):"
        buffer.indent()
        if cls.__doc__:
            buffer += f'"""{cls.__doc__}"""'

        def sig_doc(obj: Any) -> tuple[str, str | None]:
            globals = dict(sys.modules[obj.__module__].__dict__)
            type_checking_globals = {
                'Project': project.Project,
            }
            globals.update(type_checking_globals)
            try:
                signature = inspect.signature(
                    obj,
                    # globals=globals,
                    globals=type_checking_globals,
                    locals=type_checking_globals,
                )
            except (NameError, ValueError, TypeError, AttributeError) as e:
                signature = f'(~ERROR~ {e})'
            # print(annotationlib.get_annotations(obj, globals=type_checking_globals))
            doc = inspect.getdoc(obj)
            signature_str = str(signature)
            for _ in (
                    'collections.abc',
                    'pathlib',
                    'edarw.eda.librepcb',
            ):
                signature_str = signature_str.replace(_ + '.', '')
            return signature_str, doc

        members = inspect.getmembers(cls)
        for name, obj in members:
            if name.startswith('__') and name.endswith('__'):
                continue
            if name.startswith('_'):
                continue

            if inspect.isfunction(obj) or inspect.ismethod(obj):
                signature, doc = sig_doc(obj)
                # if doc:
                #     buffer += f'"""{doc}"""'
                buffer += f"def {name}{signature}: ..."
            elif isinstance(obj, property):
                signature, doc = sig_doc(obj.fget)
                buffer += "@property"
                buffer += f"def {name}{signature}: ..."

        buffer.new_line()
        annotations = annotationlib.get_annotations(cls)
        for field, type_ in annotations.items():
            is_list = hasattr(type_, '__origin__') and type_.__origin__ == builtins.list
            is_tuple = hasattr(type_, '__origin__') and type_.__origin__ == builtins.tuple
            match type_:
                case PositionalField():
                    type_str = str(type_.type)
                case _:
                    if is_list:
                        obj_type = type_.__args__[0]
                        type_str = f'list[{obj_type.__name__}]'
                    if is_tuple:
                        obj_type = ', '.join(_.__name__ for _ in type_.__args__)
                        type_str = f'tuple[{obj_type}]'
                    else:
                        type_str = type_.__name__
            buffer += "@property"
            buffer += f"def {field}(self) -> {type_str}: ..."
        mode = 'a' if pyi_path.exists() else 'w'
        print()
        print(f"Add class [blue]{cls.__name__}[/] to [red]{pyi_path}[/] {mode}")
        # with open(pyi_path, mode) as fh:
        #     fh.write(str(buffer))
        print(buffer)
