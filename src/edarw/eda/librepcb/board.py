####################################################################################################
#
# EDA-RW — Python library to read/write EDA Sexpr file format
# Copyright (C) 2026 Fabrice SALVAIRE
# SPDX-License-Identifier: AGPL-3.0-or-later
#
####################################################################################################

__all__ = ['Board']

####################################################################################################

import logging
from pathlib import Path
from typing import TYPE_CHECKING, Self, cast

from rich import print

from edarw.geometry import Position as gPosition, EuclidianMatrix
from edarw.sexpr import UUID

from .common import LibreSexpr, Position, UuidSexpr

if TYPE_CHECKING:
    from .component import Component, Gate
    from .project import Project

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

class Grid(LibreSexpr):
    CAR = 'grid'
    interval: float
    unit: str  # ['millimeters']

####################################################################################################

class Layers(LibreSexpr):
    CAR = 'layers'
    inner: int

####################################################################################################

class StopmaskClearance(LibreSexpr):
    CAR = 'stopmask_clearance'
    ratio: float
    min: float
    max: float

####################################################################################################

class SolderpasteClearance(LibreSexpr):
    CAR = 'solderpaste_clearance'
    ratio: float
    min: float
    max: float

####################################################################################################

class PadAnnularRing(LibreSexpr):
    CAR = 'pad_annular_ring'
    outer: str  # ['full']
    inner: str  # ['full']
    ratio: float
    min: float
    max: float

####################################################################################################

class ViaAnnularRing(LibreSexpr):
    CAR = 'via_annular_ring'
    ratio: float
    min: float
    max: float

####################################################################################################

class DesignRules(LibreSexpr):
    CAR = 'design_rules'
    default_trace_width: float
    default_via_drill_diameter: float
    stopmask_max_via_drill_diameter: float
    stopmask_clearance: StopmaskClearance
    solderpaste_clearance: SolderpasteClearance
    pad_annular_ring: PadAnnularRing
    via_annular_ring: ViaAnnularRing

####################################################################################################

class MaxPcbSize(LibreSexpr):
    CAR = 'max_pcb_size'
    double_sided: tuple[float, float]
    multilayer: tuple[float, float]

####################################################################################################

class DesignRuleCheck(LibreSexpr):
    CAR = 'design_rule_check'
    min_pcb_size: tuple[float, float]
    max_pcb_size: MaxPcbSize
    pcb_thickness: None
    max_layers: int
    solder_resist: None
    silkscreen: None
    min_copper_copper_clearance: float
    min_copper_board_clearance: float
    min_copper_npth_clearance: float
    min_drill_drill_clearance: float
    min_drill_board_clearance: float
    min_silkscreen_stopmask_clearance: float
    min_copper_width: float
    min_annular_ring: float
    min_npth_drill_diameter: float
    min_pth_drill_diameter: float
    min_npth_slot_width: float
    min_pth_slot_width: float
    max_tented_via_drill_diameter: float
    min_silkscreen_width: float
    min_silkscreen_text_height: float
    min_outline_tool_diameter: float
    blind_vias_allowed: bool
    buried_vias_allowed: bool
    allowed_npth_slots: str  # ['single_segment_straight']
    allowed_pth_slots: str  # ['single_segment_straight']
    approvals_version: str

####################################################################################################

class Outlines(LibreSexpr):
    CAR = 'outlines'
    suffix: str

####################################################################################################

class CopperTop(LibreSexpr):
    CAR = 'copper_top'
    suffix: str

####################################################################################################

class CopperInner(LibreSexpr):
    CAR = 'copper_inner'
    suffix: str

####################################################################################################

class CopperBot(LibreSexpr):
    CAR = 'copper_bot'
    suffix: str

####################################################################################################

class SoldermaskTop(LibreSexpr):
    CAR = 'soldermask_top'
    suffix: str

####################################################################################################

class SoldermaskBot(LibreSexpr):
    CAR = 'soldermask_bot'
    suffix: str

####################################################################################################

class SilkscreenTop(LibreSexpr):
    CAR = 'silkscreen_top'
    suffix: str

####################################################################################################

class SilkscreenBot(LibreSexpr):
    CAR = 'silkscreen_bot'
    suffix: str

####################################################################################################

class Drills(LibreSexpr):
    CAR = 'drills'
    merge: bool
    suffix_pth: str
    suffix_npth: str
    suffix_merged: str
    suffix_buried: str
    g85_slots: bool

####################################################################################################

class SolderpasteTop(LibreSexpr):
    CAR = 'solderpaste_top'
    create: bool
    suffix: str

####################################################################################################

class SolderpasteBot(LibreSexpr):
    CAR = 'solderpaste_bot'
    create: bool
    suffix: str

####################################################################################################

class FabricationOutputSettings(LibreSexpr):
    CAR = 'fabrication_output_settings'
    base_path: str
    outlines: Outlines
    copper_top: CopperTop
    copper_inner: CopperInner
    copper_bot: CopperBot
    soldermask_top: SoldermaskTop
    soldermask_bot: SoldermaskBot
    silkscreen_top: SilkscreenTop
    silkscreen_bot: SilkscreenBot
    drills: Drills
    solderpaste_top: SolderpasteTop
    solderpaste_bot: SolderpasteBot

####################################################################################################

class PreferredFootprintTags(LibreSexpr):
    CAR = 'preferred_footprint_tags'
    tht_top: None
    tht_bot: None
    smt_top: None
    smt_bot: None
    common: None

####################################################################################################

class StrokeText(UuidSexpr):
    CAR = 'stroke_text'
    layer: str  # ['top_documentation', 'top_legend']
    height: float
    stroke_width: float
    letter_spacing: str  # ['auto']
    line_spacing: ...  # {type_patterns}
    align: tuple[str, str]
    position: tuple[float, float]
    rotation: float
    auto_rotate: bool
    mirror: bool
    lock: bool
    value: str

####################################################################################################

class Device(UuidSexpr):
    CAR = 'device'
    lib_device: UUID
    lib_footprint: UUID
    lib_3d_model: UUID
    position: tuple[float, float]
    rotation: float
    flip: bool
    lock: bool
    glue: bool
    stroke_text: StrokeText

####################################################################################################

class Via(UuidSexpr):
    CAR = 'via'
    RENAMING = {'from_': 'from'}
    from_: str  # ['top_cu']
    to: str  # ['bot_cu']
    position: tuple[float, float]
    drill: float
    size: float
    exposure: str  # ['off']

####################################################################################################

class Junction(UuidSexpr):
    CAR = 'junction'
    position: tuple[float, float]

####################################################################################################

class FromMixin(LibreSexpr):
    # ['device', 'pad']
    # ['via']
    # ['junction']
    device: UUID = None  # ty: ignore[invalid-assignment]
    pad: UUID = None  # ty: ignore[invalid-assignment]
    via: UUID = None  # ty: ignore[invalid-assignment]
    junction: UUID = None  # ty: ignore[invalid-assignment]

####################################################################################################

class From(FromMixin):
    CAR = 'from'

####################################################################################################

class To(FromMixin):
    CAR = 'to'

####################################################################################################

class Trace(UuidSexpr):
    CAR = 'trace'
    RENAMING = {'from_': 'from'}
    layer: str  # ['top_cu', 'bot_cu']
    width: float
    from_: From
    to: To

####################################################################################################

class Netsegment(UuidSexpr):
    CAR = 'netsegment'
    net: UUID
    via: list[Via] = None  # ty: ignore[invalid-assignment]
    junction: list[Junction] = None  # ty: ignore[invalid-assignment]
    trace: list[Trace] = None  # ty: ignore[invalid-assignment]

####################################################################################################

class Vertex(LibreSexpr):
    CAR = 'vertex'
    position: tuple[float, float]
    angle: float

####################################################################################################

class Plane(UuidSexpr):
    CAR = 'plane'
    layer: str  # ['top_cu', 'bot_cu']
    net: UUID
    priority: int
    min_width: float
    min_copper_clearance: float
    min_board_clearance: float
    min_npth_clearance: float
    connect_style: str  # ['solid']
    thermal_gap: float
    thermal_spoke: float
    keep_islands: bool
    lock: bool
    vertex: list[Vertex]

####################################################################################################

class Polygon(UuidSexpr):
    CAR = 'polygon'
    layer: str  # ['brd_outlines']
    width: float
    fill: bool
    grab_area: bool
    lock: bool
    vertex: list[Vertex]

####################################################################################################

class Board(UuidSexpr):
    CAR = 'librepcb_board'
    name: str
    default_font: str
    grid: Grid
    layers: Layers
    thickness: float
    solder_resist: str  # ['green']
    silkscreen: str  # ['white']
    silkscreen_layers_top: tuple[str, str]
    silkscreen_layers_bot: tuple[str, str]
    design_rules: DesignRules
    design_rule_check: DesignRuleCheck
    fabrication_output_settings: FabricationOutputSettings
    preferred_footprint_tags: PreferredFootprintTags
    device: list[Device]
    netsegment: list[Netsegment]
    plane: list[Plane]
    polygon: Polygon
    stroke_text: list[StrokeText]
