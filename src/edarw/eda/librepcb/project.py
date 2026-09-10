####################################################################################################
#
# EDA-RW — Python library to read/write EDA Sexpr file format
# Copyright (C) 2026 Fabrice SALVAIRE
# SPDX-License-Identifier: AGPL-3.0-or-later
#
####################################################################################################

__all__ = ['Project']

####################################################################################################

import logging
from collections.abc import ValuesView
from datetime import datetime
from pathlib import Path

from edarw.sexpr import UUID, Positional, SexprWrapper

from .circuit import Circuit
from .component import Component

# from rich import print

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

class Project(SexprWrapper):

    """Class to read a LibrePCB Project"""

    CAR = 'librepcb_project_metadata'
    uuid: Positional[UUID]
    name: str
    author: str
    version: str
    created: datetime

    _logger = _module_logger.getChild('Project')

    ##############################################

    @classmethod
    def load(self, path: Path | str) -> Self:  # ty: ignore[invalid-method-override]
        project_path = Path(path)
        metadata_path = project_path / 'project/metadata.lp'
        return super().load(metadata_path, project_path=project_path)

    ##############################################

    def __init__(self, sexpr: list, project_path: Path) -> None:
        super().__init__(sexpr)
        self._project_path = project_path
        self._circuit: Circuit | None = None
        self._components: dict[UUID, Component] = {}
        self._load_library()

    ##############################################

    @property
    def project_path(self) -> Path:
        return self._project_path

    ##############################################

    def _load_library(self) -> None:
        library_path = self._project_path / 'library'
        cmp_path = library_path / 'cmp'
        for component_dir in cmp_path.iterdir():
            # component_uuid = component_dir.name
            component_path = component_dir / 'component.lp'
            component = Component.load(component_path, self)
            self._components[component.uuid] = component

    def component(self, uuid: UUID) -> Component:
        return self._components[uuid]

    @property
    def components(self) -> ValuesView[Component]:
        return self._components.values()

    ##############################################

    @property
    def circuit(self) -> Circuit:
        if self._circuit is None:
            circuit_path = self._project_path / 'circuit/circuit.lp'
            self._circuit = Circuit.load(circuit_path, self)
        return self._circuit
