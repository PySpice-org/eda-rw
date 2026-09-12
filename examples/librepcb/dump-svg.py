####################################################################################################
#
# EDA-RW — Python library to read/write EDA Sexpr file format
# Copyright (C) 2021 Fabrice SALVAIRE
# SPDX-License-Identifier: AGPL-3.0-or-later
#
####################################################################################################

from pathlib import Path

from rich import print
from rich.console import Console

from edarw.geometry import Position as gPosition, EuclidianMatrix, Vector
from edarw.eda.librepcb import Project
from edarw.eda.librepcb.common import LibreSexpr
from edarw.log import setup_logging

import svg

####################################################################################################

logger = setup_logging()

console = Console()

####################################################################################################

path = Path('../../librepcb-examples/calidou')
project: Project = Project.load(path)

elements = []

schematic = project.schematic
circuit = project.circuit
# LibreSexpr.dump_uuids()

# print(schematic.to_json())

symbol_center_color = 'red'
symbol_color = 'black'
pin_color = 'black'
net_color = 'blue'
junction_color = 'blue'

for netsegment in schematic.netsegment:
    for line in netsegment.line:
        x1, y1 = line.from_.position.xy
        x2, y2 = line.to.position.xy
        segment = svg.Line(
          x1=x1, x2=x2,
          y1=y1, y2=y2,
          stroke=net_color,
          stroke_width=line.width,
          stroke_linecap='round',
        )
        elements.append(segment)

    for junction in netsegment.junction:
        x, y = junction.position
        circle = svg.Circle(
            cx=x, cy=y,
            r=.2,
            stroke='none',
            fill=junction_color,
            stroke_width=0,
            opacity=.3,
        )
        elements.append(circle)

for symbol in schematic.symbol:
    console.rule()

    # print(symbol.to_json())
    component = symbol.component_obj  # circuit.Component
    gate = symbol.lib_gate_obj  # component.Gate
    # drawing is define in symbol.lp:
    symbol_def = gate.symbol_obj  # symbol.Symbol
    # print(component.to_json())
    # print(gate.to_json())
    # print(symbol_def.to_json())

    print(f"{symbol_def.name} mirror={symbol.mirror}")

    if 'Frame' in symbol_def.name:
        continue

    offset = symbol.position_obj
    rotation = EuclidianMatrix.rotation(symbol.rotation)
    if symbol.mirror:
        rotation = rotation.xy_mirror

    def symbol_transform(position: gPosition) -> gPosition:
        return position * rotation + offset

    for polygon in symbol_def.polygon:
        if polygon.layer in ('sym_hidden_grab_areas',):
            continue
        positions = [_.position_obj * rotation + offset for _ in polygon.vertex]
        points = []
        for _ in positions:
            points += _.xy
        polygon = svg.Polygon(
            points=points,
            stroke=symbol_color,
            fill=symbol_color if polygon.fill else 'none',
            stroke_width=polygon.width,
            stroke_linejoin='round',
        )
        elements.append(polygon)

    for pin in symbol_def.pin:
        x, y = symbol_transform(pin.position_obj).xy
        position2 = pin.position_obj + Vector.direction(pin.length, pin.rotation)
        x2, y2 = symbol_transform(position2).xy
        segment = svg.Line(
          x1=x, x2=x2,
          y1=y, y2=y2,
          stroke=pin_color,
          stroke_width=.1,
          stroke_linecap='round',
        )
        elements.append(segment)
        circle = svg.Circle(
            cx=x, cy=y,
            r=.2,
            stroke='nonde',
            fill=pin_color,
            stroke_width=0,
            opacity=.3,
        )
        elements.append(circle)

    # symbol position
    x, y = symbol.position
    circle = svg.Circle(
        cx=x, cy=y,
        r=.2,
        stroke='none',
        fill=symbol_center_color,
        stroke_width=0,
    )
    elements.append(circle)

canvas = svg.SVG(
    # width=60,
    # height=60,
    elements=[
        svg.G(
            transform=svg.Matrix(1, 0, 0, -1, 0, 100),
            elements=elements,
        ),
    ]
)
svg_path = Path('schema.svg')
svg_path.write_text(str(canvas))
