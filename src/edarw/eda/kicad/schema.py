####################################################################################################
#
# EDA-RW — Python library to read/write EDA Sexpr file format
# Copyright (C) 2021 Fabrice SALVAIRE
# SPDX-License-Identifier: AGPL-3.0-or-later
#
####################################################################################################

"""This module implements a KiCad 6 schema file format parser (`.kicad_sch` file extension) and an
algorithm to guess the netlist from the schematic.

This is a work in progress.  Actually, it only retrieves useful data to generate a netlist.

Since version 6, KiCad uses for schematic a file format based on the Specctra DSN file format.  It
is based on `S-expression <https://en.wikipedia.org/wiki/S-expression`_, also called symbolic
expressions and abbreviated as sexprs, is a notation for nested list (tree-structured) data,
invented for and popularized by the programming language Lisp.

To understand what contain the file, you must understand this format is roughly equivalent to a SVG
export of the schematic, with additional information like the value and footprint of a symbol.  The
data are thus purely graphical.  When you draw a schematic on KiCad, you are just drawing and not
building a graph.

Notice this code implements many tricks to handle this file format:

- We cannot validate the format using a kind of DTD.
- S-expression support is quite limited in comparison to XML libraries.  The sexpdata Python module
  provides data at a very low level in comparison to XML and even JSON/YAML.  For example, there is
  no XPath feature, no tool to deserialise to an oriented object API, and no linter.
- It is unclear how it would be easy to change data and rewrite a file.
- KiCad don't store fundamental information like the netlist, thus we have to guess it using object coordinates.
- KiCad uses localised property names, e.g. for sheet filename.  The key will be in French if you
  saved the file with the UI language set to French.

Why the hell, KiCad don't use an XML file format and don't store the netlist !

"""

####################################################################################################

__all__ = [
    'KiCadSchema',
]

####################################################################################################

import logging
from collections.abc import Iterable, Iterator
from itertools import combinations
from typing import Any

from edarw.geometry import EuclidianMatrice, Position, PositionAngle, Vector

# Fixme: use sexpdata ???
from .deprecated.sexpression import Sexpression, car_value, cdr

####################################################################################################

_module_logger = logging.getLogger(__name__)

####################################################################################################

type Pair = tuple[Any, Any]
type FloatPair = tuple[float, float]
type StrPair = tuple[str, str]

####################################################################################################

def pairwise(iterable: Iterable) -> Iterator:
    yield from combinations(iterable, 2)

def exchange_pair(_: Pair) -> Pair:
    return (_[1], _[0])

####################################################################################################

class NameMixin:

    ##############################################

    def __init__(self, name: str) -> None:
        self._name = name

    ##############################################

    def __hash__(self) -> int:
        return hash((self.__class__.__name__, self._name))

    ##############################################

    @property
    def name(self) -> str:
        return self._name

    @property
    def full_name(self) -> str:
        return f"{self.__class__.__name__} {self._name}"

####################################################################################################

class NumberNameMixin(NameMixin):

    ##############################################

    def __init__(self, number: int, name: str) -> None:
        self._number = number
        NameMixin.__init__(self, name)

    ##############################################

    @property
    def number(self) -> int:
        return self._number

    @property
    def name(self) -> str:
        return self._name

####################################################################################################

class OnWireMixin(Position):

    ##############################################

    def __init__(self, x: float, y: float) -> None:
        super().__init__(x, y)
        self._wires: set[Wire] = set()

    ##############################################

    @property
    def wires(self) -> Iterator[Wire]:
        return iter(self._wires)

    ##############################################

    def connect_wire(self, wire: Wire) -> None:
        self._wires.add(wire)

    ##############################################

    def match_wires(self, wires: Iterable[Wire]) -> None:
        for wire in wires:
            if wire.contains(self):
                self.connect_wire(wire)

####################################################################################################

class NetMixin:

    ##############################################

    def __init__(self) -> None:
        self._net: Net | None = None

    ##############################################

    @property
    def net(self) -> Net | None:
        return self._net

    # we need this checked version for typing
    @property
    def inet(self) -> Net:
        if self._net is None:
            raise NameError("Net is uninitialized")
        return self._net

    @net.setter
    def net(self, net: Net) -> None:
        self._net = net

####################################################################################################

class Pin(NumberNameMixin, Position):

    """Class to implement a pin of a symbol"""

    ##############################################

    def __init__(self, number: int, name: str, x: float, y: float) -> None:
        Position.__init__(self, x, y)
        NumberNameMixin.__init__(self, number, name)

    ##############################################

    def __str__(self) -> str:
        return f"Pin f{self._number} " + super().__str__()

####################################################################################################

class PinPosition(NumberNameMixin, NetMixin, Position):

    """Class to implement a pin of a symbol instance"""

    # Fixme: name ???

    ##############################################

    def __init__(self, symbol: Symbol, number: int, name: str, x: float, y: float) -> None:
        self._symbol = symbol
        Position.__init__(self, x, y)
        NumberNameMixin.__init__(self, number, name)
        NetMixin.__init__(self)

    ##############################################

    def __hash__(self) -> int:
        return hash(self.full_name)

    ##############################################

    @property
    def full_name(self) -> str:
        # {self.__class__.__name__}
        return f"{self._symbol.reference}/{self._number}"

    ##############################################

    def __str__(self) -> str:
        return f"Pin Position #{self._number} net #{self.net} " + super().__str__()

####################################################################################################

class SymbolLib(NameMixin):

    """Class to implement a symbol in a library"""

    ##############################################

    def __init__(self, name: str) -> None:
        NameMixin.__init__(self, name)
        self._pins: list[Pin] = []

    ##############################################

    @property
    def pins(self) -> Iterator[Pin]:
        return iter(self._pins)

    ##############################################

    def add_pin(self, number: int, name: str, x: float, y: float) -> None:
        pin = Pin(number, name, x, y)
        self._pins.append(pin)
        # return pin

####################################################################################################

class Symbol(PositionAngle):

    """Class to implement a symbol instance"""

    _logger = _module_logger.getChild('Symbol')

    ##############################################

    def __init__(
        self,
        lib: SymbolLib,
        x: float, y: float, angle: int,
        unit: int,
        in_bom: bool = True,
        on_board: bool = True,
        reference: str = '', value: str = '',
        footprint: str = '',
        datasheet: str = '',
        simulation_device: str = '',
        simulation_type: str = '',
        simulation_paramaters: str = '',
        simulation_pins: str = '',
        mirror: str | None = None,  # optional
    ) -> None:
        # Fixme: uuid
        super().__init__(x, y, angle)
        self._lib = lib
        self._mirror = mirror  # Fixme: None ???
        self._unit = unit
        self._in_bom = in_bom
        self._on_board = on_board
        self._reference = reference
        self._value = value
        self._footprint = footprint
        self._datasheet = datasheet
        self._simulation_device = simulation_device
        self._simulation_type = simulation_type
        self._simulation_paramaters = simulation_paramaters
        self._simulation_pins = simulation_pins
        self._pins = [self._pin_position(pin) for pin in self._lib.pins]

    ##############################################

    @property
    def lib(self) -> SymbolLib:
        return self._lib

    @property
    def lib_name(self) -> str:
        return self._lib.name

    @property
    def mirror(self) -> str | None:
        return self._mirror

    @property
    def unit(self) -> int:
        return self._unit

    @property
    def in_bom(self) -> bool:
        return self._in_bom

    @property
    def on_board(self) -> bool:
        return self._on_board

    @property
    def reference(self) -> str:
        return self._reference

    @property
    def value(self) -> str:
        return self._value

    @property
    def footprint(self) -> str:
        return self._footprint

    @property
    def datasheet(self) -> str:
        return self._datasheet

    @property
    def simulation_device(self) -> str:
        return self._simulation_device

    @property
    def simulation_type(self) -> str:
        return self._simulation_type

    @property
    def simulation_paramaters(self) -> str:
        return self._simulation_paramaters

    @property
    def simulation_pins(self) -> str:
        return self._simulation_pins

    @property
    def pins(self) -> Iterator[PinPosition]:
        return iter(self._pins)

    @property
    def first_pin(self) -> PinPosition:
        return self._pins[0]

    ##############################################

    @property
    def full_name(self) -> str:
        return f"{self.__class__.__name__} {self._reference}"

    ##############################################

    def _unassigned_pins(self) -> Iterator[PinPosition]:
        for pin_position in self._pins:
            if pin_position.net is None:
                yield pin_position

    ##############################################

    # it depends how is draw the symbol...
    # @property
    # def direction(self):
    #     if self._angle == 0:
    #         return 'up'
    #     elif self._angle == 90:
    #         return 'right'
    #     elif self._angle == 180:
    #         return 'left'
    #     elif self._angle == 270:
    #         return 'down'

    ##############################################

    def _pin_position(self, pin: Pin) -> PinPosition:
        """Compute the pin position in the sheet"""
        v = Vector(pin.x, -pin.y)
        # angle = self._angle
        matrice = EuclidianMatrice.rotation(self._angle)
        match self._mirror:
            case 'x':
                matrice = EuclidianMatrice.x_mirror(matrice)
            case 'y':
                matrice = EuclidianMatrice.y_mirror(matrice)
        p = v * matrice + self
        return PinPosition(self, pin.number, pin.name, p.x, p.y)

    ##############################################

    def match_pin_with_wire(self, wires: Iterable[Wire]) -> None:
        for pin in self._pins:
            for wire in wires:
                if wire.match_position(pin):
                    self._logger.info(f"Pin {self._reference}/{pin.number} is on wire {wire.id}")
                    wire.inet.link(pin)
            # if pin.net is None:
            #     self._logger.warning(f"Net not found {self.reference} pin #{pin.number}")

    ##############################################

    def match_pin_with_pin(self, symbols: Iterable[Symbol]) -> None:
        for pin in self._unassigned_pins():
            for symbol in symbols:
                if symbol is self:
                    continue
                for pin2 in symbol.pins:
                    if pin == pin2:
                        self._logger.info(
                            f"Pin {self._reference}/{pin.number} is connected to {symbol.reference}/{pin2.number}"
                        )
                        match pin.net, pin2.net:
                            case None, None:
                                net = Net(item=pin)
                                net.link(pin2)
                            case Net(), None:
                                pin.net.link(pin2)
                            case None, Net():
                                pin2.net.link(pin)
                            case Net(), Net():
                                pin.merge(pin2)  # ty: ignore[unresolved-attribute]
            if pin.net is None:
                self._logger.warning(f"Net not found for pin {self.reference}/{pin.number}")

####################################################################################################

# class WireJunction:
#     def __init__(self, wire1: Wire, wire2: Wire) -> None:
#         self.wire1 = wire1
#         self.wire2 = wire2

####################################################################################################

class Wire(NetMixin):

    _logger = _module_logger.getChild('Wire')

    ##############################################

    def __init__(self, id: int, start_point: FloatPair, end_point: FloatPair) -> None:
        NetMixin.__init__(self)
        self._id = id
        self._start = Position(*start_point)
        self._end = Position(*end_point)
        u = self._end - self._start
        if u.is_vertical:
            self._direction = 'V'
        elif u.is_horizontal:
            self._direction = 'H'
        else:
            self._direction = None

        self._connections: set[Wire] = set()
        self._connection_types: set[tuple[Wire, StrPair]] = set()
        self.label = None

    ##############################################

    def __hash__(self) -> int:
        return hash((self.__class__.__name__, self._id))

    ##############################################

    @property
    def id(self) -> int:
        return self._id

    @property
    def start(self) -> Position:
        return self._start

    @property
    def end(self) -> Position:
        return self._end

    @property
    def direction(self) -> str | None:
        return self._direction

    ##############################################

    @property
    def full_name(self) -> str:
        return f"{self.__class__.__name__} {self._id}"

    ##############################################

    @property
    def connections(self) -> set[Wire]:
        return self._connections

    ##############################################

    # we had to duplicate the definition from NetMixin for @net.setter
    @property
    def net(self) -> Net | None:
        return self._net

    @net.setter
    def net(self, net: Net) -> None:
        # if net is None:
        #     raise NetError
        if self._net is None:
            self._net = net
            for _ in self._connections:
                # _.net = net
                net.link(_)
        elif self._net != net:
            raise NameError(f"wire on net {self._net} overwritten to {net}")

    ##############################################

    def __str__(self) -> str:
        direction = ''
        if self._direction == 'V':
            direction = 'vertical'
        elif self._direction == 'H':
            direction = 'horizontal'
        _ = f"{self.__class__.__name__} #{self._id}"
        _ += f"from {self._start} to {self._end} dir={direction} on net {self.net}"
        return _

    ##############################################

    def match_position(self, position: Position) -> bool:
        return self._start == position or self._end == position

    ##############################################

    def match_extremities(self, wire: Wire) -> bool:
        connection = None
        if self._start == wire.start:
            connection = ('s', 's')
        elif self._start == wire.end:
            connection = ('s', 'e')
        elif self._end == wire.start:
            connection = ('e', 's')
        elif self._end == wire.end:
            connection = ('e', 'e')
        if connection is not None:
            self._logger.info(f"Wire {self._id} is connected to {wire.id}")
            self.add_connection(wire, connection)
            wire.add_connection(self, exchange_pair(connection))
            return True
        return False

    ##############################################

    def contains(self, obj: Position) -> bool:
        return Vector.point_in_segment(self._start, self._end, obj)

    ##############################################

    def add_connection(self, wire: Wire, type_: StrPair) -> None:
        if wire is self:
            self._logger.warning("self connection")
        else:
            self._connections.add(wire)
            self._connection_types.add((wire, type_))

    ##############################################

    # @classmethod
    # def connect(cls, wires):
    #     if len(wires) > 1:
    #         for _ in wires:
    #             _.add_connections(wires)

    ##############################################

    # def add_connections(self, wires):
    #     for _ in wires:
    #         self.add_connection(_)

####################################################################################################

class Bus(Wire):
    pass

####################################################################################################

class Junction(OnWireMixin):

    _logger = _module_logger.getChild('Junction')

    ID = 0

    ##############################################

    def __init__(self, x: float, y: float) -> None:
        super().__init__(x, y)
        Junction.ID += 1   # Fixme: atomic
        self._id = Junction.ID
        self._connection_types = {}

    ##############################################

    @property
    def id(self) -> int:
        # Fixme: mixin
        return self._id

    ##############################################

    def __str__(self) -> str:
        return f"Junction {self._id} at " + super().__str__()

    ##############################################

    def match_wires(self, wires: Iterable[Wire]) -> None:
        for wire in wires:
            connection = None
            if wire.start == self:
                connection = 's'
            elif wire.end == self:
                connection = 'e'
            elif wire.contains(self):
                connection = 'j'
            if connection is not None:
                self.connect_wire(wire)
                self._connection_types[wire.id] = connection
        # connect wires
        for wire1, wire2 in pairwise(self._wires):
            self._logger.debug(f"Junction {self._id} on wire {wire1.id} and {wire2.id}")
            connection = tuple([self._connection_types[_.id] for _ in (wire1, wire2)])
            wire1.add_connection(wire2, connection)
            wire2.add_connection(wire1, connection)

####################################################################################################

class NoConnect(OnWireMixin):

    ##############################################

    def __str__(self) -> str:
        return "No connect at " + super().__str__()

####################################################################################################

class BusEntry(OnWireMixin):

    # Fixme: bus

    ##############################################

    def __str__(self) -> str:
        return "Bus entry at " + super().__str__()

####################################################################################################

class Label(NameMixin, OnWireMixin, NetMixin):

    _logger = _module_logger.getChild('Label')

    ##############################################

    def __init__(self, name: str, x: float, y: float) -> None:
        OnWireMixin.__init__(self, x, y)
        NameMixin.__init__(self, name)
        NetMixin.__init__(self)

    ##############################################

    def __str__(self) -> str:
        return f"Label {self._name} " + super().__str__()

    ##############################################

    def connect_wire(self, wire: Wire) -> None:
        # Fixme: GlobalLabel HierarchicalLabel
        self._logger.info(f"Wire {wire.id} has label {self._name}")
        super().connect_wire(wire)
        wire.label = self

    ##############################################

    def make_net(self) -> None:
        self._logger.info(f"Make net {self._name}")
        net = Net(id=self._name, item=self)
        # self.net = net
        for wire in self._wires:
            # wire.net = net
            net.link(wire)

####################################################################################################

class GlobalLabel(Label):

    ##############################################

    def __str__(self) -> str:
        return f"Global label f{self._name} " + super().__str__()

####################################################################################################

class HierarchicalLabel(Label):

    ##############################################

    def __str__(self) -> str:
        return f"Hierarchical label f{self._name} " + super().__str__()

####################################################################################################

class Sheet:
    pass

####################################################################################################

class Net:

    """Class to implemenent a net in a circuit.

    A net can be a set of:
    - wires connected by extremities, junctions, or labels
    - pin connected to a wire or another pin
    """

    _logger = _module_logger.getChild('Net')

    UUID = 0
    NETS: list[Net] = []
    MAP: dict[int | str, Net] = {}

    ##############################################

    @classmethod
    def assign_ids(cls):
        _id = 1
        for net in cls.NETS:
            if net._id is None:
                cls._logger.info(f"Assign {_id} to UUID={net._uuid}")
                net._id = _id
                cls.MAP[_id] = net
                _id += 1

    ##############################################

    def __init__(self, id: int | str | None = None, item: Any = None) -> None:
        Net.NETS.append(self)
        Net.UUID += 1   # Fixme: Atomic
        self._uuid = Net.UUID
        self._logger.info(f"New Net UUID={self._uuid} ID={id}")
        self._id: int | str | None = None
        if id is not None:
            self.id = id
        self._items = set()
        if item is not None:
            self.link(item)

    ##############################################

    def link(self, item: PinPosition | Label | Wire) -> None:
        # Fixme: complete typing ???
        # Fixme: API ???
        #   recursive ???
        if item.net != self:
            self._logger.info(f"Link net UUID={self._uuid} and item {item.full_name}")
            item.net = self
            self._items.add(item)
            # print(self.uuid, [_.full_name for _ in self._items])

    ##############################################

    @property
    def uuid(self) -> int:
        return self._uuid

    ##############################################

    @property
    def id(self) -> int | str | None:
        return self._id

    @id.setter
    def id(self, value: int | str) -> None:
        if value not in Net.MAP:
            self._logger.info(f"Set ID={value} to UUID={self._uuid}")
            self._id = value
            Net.MAP[value] = self
        else:
            raise NameError(f"Id {value} is already assigned")

    ##############################################

    def __str__(self) -> str:
        if self._id is None:
            return f"Net UUID={self._uuid}"
        else:
            return f"Net ID={self._id} UUID={self._uuid}"

    ##############################################

    def merge(self, net: Net) -> None:
        self._logger.info(f"Merge net {net._uuid} to {self._uuid}")
        for item in net._items:
            self.link(item)

####################################################################################################

class KiCadSchema(Sexpression):

    """Class to read a KiCad Schema"""

    _logger = _module_logger.getChild('KiCadSchema')

    GROUND_SYMBOLS = (
        # 'spice-ngspice:0',
        'power:GND',
    )

    ##############################################

    def __init__(self, path) -> None:
        self._symbol_libs = {}
        self._wires: list[Wire] = []
        self._buses: list[Bus] = []
        self._junctions: list[Junction] = []
        self._no_connections: list[NoConnect] = []
        self._bus_entries: list[BusEntry] = []
        self._labels: list[Label] = []
        self._global_labels: list[GlobalLabel] = []
        self._hierarchical_labels: list[HierarchicalLabel] = []
        self._symbols: list[Symbol] = []
        self._sheets: list[Sheet] = []

        self._read(path)
        self._make_netlist()

    ##############################################

    @property
    def symbol_libs(self):
        return iter(self._symbol_libs)

    @property
    def symbols(self) -> Iterator[Symbol]:
        return iter(self._symbols)

    @property
    def symbols_by_reference(self):
        yield from sorted(self._symbols, key=lambda _: _.reference)

    @property
    def symbols_by_position(self):
        yield from sorted(self._symbols, key=lambda _: f"{_.x:.2f}{_.y:.2}")

    @property
    def wires(self) -> Iterator[Wire]:
        return iter(self._wires)

    @property
    def buses(self) -> Iterator[Bus]:
        return iter(self._buses)

    @property
    def junctions(self) -> Iterator[Junction]:
        return iter(self._junctions)

    @property
    def no_connections(self) -> Iterator[NoConnect]:
        return iter(self._no_connections)

    @property
    def bus_entries(self) -> Iterator[BusEntry]:
        return iter(self._bus_entries)

    @property
    def labels(self) -> Iterator[Label]:
        return iter(self._labels)

    @property
    def global_labels(self) -> Iterator[GlobalLabel]:
        return iter(self._global_labels)

    @property
    def hierarchical_labels(self) -> Iterator[HierarchicalLabel]:
        return iter(self._hierarchical_labels)

    ##############################################

    def _read(self, path: str) -> None:
        self._logger.info(f"Load KiCad schema {path}")
        s_data = self.load(path)

        if car_value(s_data) != 'kicad_sch':
            raise ValueError()

        for sexpr in cdr(s_data):
            _car_value = car_value(sexpr)
            print(_car_value, type(_car_value))
            match _car_value:
                case 'version':
                    # ('version', 20210406)
                    self._version = cdr(sexpr)
                case 'generator':
                    # ('generator', 'eeschema')
                    self._generator = cdr(sexpr)
                case 'uuid':
                    # ('uuid', 'ca1ca076-e632-4fcc-8412-0a7bfcb4ba0b')
                    self._uuid = cdr(sexpr)
                case 'paper':
                    # ('paper', 'A4')
                    self._paper = cdr(sexpr)
                case 'lib_symbols':
                    for s_symbol in cdr(sexpr):
                        self._on_lib_symbol(s_symbol)
                case 'junction':
                    # ('junction', ('at', 111.76, 73.66), ('diameter', 1.016), ('color', 0, 0, 0, 0))
                    _, d = self.to_dict(sexpr)
                    junction = Junction(*d['at'])
                    self._junctions.append(junction)
                case 'no_connect':
                    # (no_connect (at 177.8 50.8) (uuid b47f754e-304e-4f98-968e-20e5e5d18e29))
                    _, d = self.to_dict(sexpr)
                    no_connection = NoConnect(*d['at'])
                    self._no_connections.append(no_connection)
                case 'bus_entry':
                    # (bus_entry (at 190.5 80.01) (size 2.54 2.54)
                    #   (stroke (width 0.1524) (type solid) (color 0 0 0 0))
                    #   (uuid 55cddc77-72fd-4412-84fa-867166598c36)
                    # )
                    _, d = self.to_dict(sexpr)
                    bus_entry = BusEntry(*d['at'])
                    self._bus_entries.append(bus_entry)
                case 'wire':
                    # 'wire',
                    #     ('pts', ('xy', 140.97, 73.66), ('xy', 144.78, 73.66)),
                    #     ('stroke', ('width', 0), ('type', 'solid'), ('color', 0, 0, 0, 0)),
                    #     ('uuid', '53b6c7f9-e319-4bc4-82b5-f7c696f8e2db')
                    _, d = self.to_dict(sexpr)
                    self.fix_key_as_list(d['pts'], 'xy', 'xys')
                    start_point, end_point = d['pts']['xys']
                    wire = Wire(len(self._wires), start_point, end_point)
                    self._wires.append(wire)
                case 'bus':
                    # (bus (pts (xy 101.6 81.28) (xy 127 81.28))
                    #    (stroke (width 0) (type solid) (color 0 0 0 0))
                    #    (uuid 1029c8b7-917c-4b83-8b82-040bab29659a)
                    #  )
                    _, d = self.to_dict(sexpr)
                    self.fix_key_as_list(d['pts'], 'xy', 'xys')
                    start_point, end_point = d['pts']['xys']
                    bus = Bus(len(self._buses), start_point, end_point)
                    self._buses.append(bus)
                case 'label':
                    # (label "out" (at 134.62 86.36 180)
                    #   (effects (font (size 1.27 1.27)) (justify right bottom))
                    #   (uuid d18a8a30-fded-4d73-acd2-a0615b9eda55)
                    # )
                    _, d = self.to_dict(sexpr)
                    name = self.sattr(d)
                    at = d['at'][:2]
                    label = Label(name, *at)
                    self._labels.append(label)
                case 'global_label':
                    # (global_label "Ground" (shape input) (at 114.3 114.3 180) (fields_autoplaced)
                    #   (effects (font (size 1.27 1.27)) (justify right))
                    #   (uuid 2d598105-6602-42a5-9940-1d3919aba7e9)
                    #   (property "Intersheet References" "${INTERSHEET_REFS}" (id 0) (at 105.2345 114.2206 0)
                    #     (effects (font (size 1.27 1.27)) (justify right) hide)
                    #   )
                    # )
                    _, d = self.to_dict(sexpr)
                    name = self.sattr(d)
                    global_label = GlobalLabel(name, *d['at'])
                    self._global_labels.append(global_label)
                case 'hierarchical_label':
                    # (hierarchical_label "W3" (shape input) (at 228.6 50.8 0)
                    #   (effects (font (size 1.27 1.27)) (justify left))
                    #   (uuid 2f06b05a-b838-4b5e-be45-45567e9ea945)
                    # )
                    _, d = self.to_dict(sexpr)
                    name = self.sattr(d)
                    hierarchical_label = HierarchicalLabel(name, *d['at'])
                    self._hierarchical_labels.append(hierarchical_label)
                case 'symbol':
                    self._on_symbol(sexpr)
                case 'sheet':
                    # (sheet (at 76.2 76.2) (size 25.4 25.4) (fields_autoplaced)
                    #   (stroke (width 0.0006) (type solid) (color 0 0 0 0))
                    #   (fill (color 0 0 0 0.0000))
                    #   (uuid c25a1926-29f6-4d91-8c26-f75c9c7dff11)
                    #   (property "Nom feuille" "Sheet1" (id 0) (at 76.2 75.5643 0)
                    #     (effects (font (size 1.27 1.27)) (justify left bottom))
                    #   )
                    #   (property "Fichier de feuille" "sheet1.kicad_sch" (id 1) (at 76.2 102.1087 0)
                    #     (effects (font (size 1.27 1.27)) (justify left top))
                    #   )
                    #   (pin "W1" input (at 101.6 81.28 0)
                    #     (effects (font (size 1.27 1.27)) (justify right))
                    #     (uuid b0424fd4-3d1f-4f3b-be2f-1ff8781c6ef2)
                    #   )
                    # )
                    pass
                case 'sheet_instances':
                    # (sheet_instances
                    #   (path "/" (page "1"))
                    #   (path "/c25a1926-29f6-4d91-8c26-f75c9c7dff11" (page "2"))
                    #   (path "/ee43db97-511c-42d6-92c0-c5fecfe9c5f6" (page "3"))
                    # )
                    pass
                case 'symbol_instances':
                    # (symbol_instances
                    #   (path "/52705c8a-fed0-4f7d-8870-412cce75c251"
                    #     (reference "#PWR0101") (unit 1) (value "GND") (footprint "")
                    #   )
                    #   (path "/c25a1926-29f6-4d91-8c26-f75c9c7dff11/0e0e3bc6-dd31-4ee9-83c4-2b06632480b0"
                    #     (reference "R1") (unit 1) (value "R") (footprint "")
                    #   )
                    #   (path "/ee43db97-511c-42d6-92c0-c5fecfe9c5f6/219580f3-4290-4b55-9258-083dd190dd5a"
                    #     (reference "R2") (unit 1) (value "R") (footprint "")
                    #   )
                    # )
                    pass
                case 'embedded_fonts':
                    pass
                case 'generator_version':
                    pass
                case _:
                    raise ValueError(f'Unknown car {_car_value}')

    ##############################################

    def _on_lib_symbol(self, sexpr):
        # 'symbol',
        #     'spice-ngspice:C',
        #     ('pin_names', ('offset', 0.254)),
        #     ('in_bom', 'yes'),
        #     ('on_board', 'yes'),
        #     ('property', 'Reference', 'C',
        #         ('id', 0), ('at', 0, 1.016, 0),
        #         ('effects', ('font', ('size', 1.27, 1.27)),
        #         ('justify', 'left', 'bottom'))),
        #     ('property', 'Value', 'C',
        #         ('id', 1), ('at', 0, -1.27, 0),
        #         ('effects', ('font', ('size', 1.27, 1.27)),
        #         ('justify', 'left', 'top'))),
        #     ('property', 'Footprint', '',
        #         ('id', 2), ('at', 0, 0, 0),
        #         ('effects', ('font', ('size', 1.524, 1.524)))),
        #     ('property', 'Datasheet', '', ('id', 3), ('at', 0, 0, 0),
        #         ('effects', ('font', ('size', 1.524, 1.524)))),
        #     ('symbol', 'C_0_1',
        #         ('polyline', ('pts', ('xy', -2.54, -0.635), ('xy', 2.54, -0.635)),
        #             ('stroke', ('width', 0)), ('fill', ('type', 'none'))),
        #         ('polyline', ('pts', ('xy', -2.54, 0.635), ('xy', 2.54, 0.635)),
        #             ('stroke', ('width', 0)), ('fill', ('type', 'none')))
        #     ),
        #     ('symbol', 'C_1_1',
        #          ('pin',
        #              'passive',
        #              'line',
        #              ('at', 0, 2.54, 270),
        #              ('length', 1.905),
        #              ('name', '~', ('effects', ('font', ('size', 0.254, 0.254)) )),
        #              ('number', '1', ('effects', ('font', ('size', 0.254, 0.254))))
        #          ),
        #          ('pin',
        #              'passive',
        #              'line',
        #              ('at', 0, -2.54, 90),
        #              ('length', 1.905),
        #              ('name', '~', ('effects', ('font', ('size', 0.254, 0.254)))),
        #              ('number', '2', ('effects', ('font', ('size', 0.254, 0.254)))
        #          )
        #     )
        # )

        _, d = self.to_dict(sexpr)
        self.fix_key_as_dict(d, 'property', 'properties')
        self.fix_key_as_dict(d, 'symbol', 'symbols')
        for _ in d['symbols'].values():
            self.fix_key_as_list(_, 'polyline', 'polylines')
            self.fix_key_as_list(_, 'pin', 'pins')

        name = self.sattr(d)
        symbol_lib = SymbolLib(name)
        self._symbol_libs[name] = symbol_lib
        # kind of XPath to get pins...
        for d1 in d['symbols'].values():
            for key, d2 in d1.items():
                if key == 'pins':
                    for spin in d2:
                        number = int(self.sattr(spin['number']))
                        name = self.sattr(spin['name'])
                        at = spin['at'][:2]
                        symbol_lib.add_pin(number, name, *at)

    ##############################################

    def _on_symbol(self, sexpr) -> None:
        # 'symbol',
        #     ('lib_id', 'spice-ngspice:R'),
        #     ('at', 116.84, 78.74, 270),
        #     ('mirror', 'x'),
        #     ('unit', 1),
        #     ('in_bom', 'yes'),
        #     ('on_board', 'yes'),
        #     ('uuid', '00000000-0000-0000-0000-00006099a2a1'),
        #     ('property', 'Reference', 'Remi1', ('id', 0), ('at', 116.84, 82.55, 90)),
        #     ('property', 'Value', '165k', ('id', 1), ('at', 116.84, 85.09, 90)),
        #     ('property', 'Footprint', '', ('id', 2), ('at', 116.84, 78.74, 0),
        #                           ('effects', ('font', ('size', 1.524, 1.524)))),
        #     ('property', 'Datasheet', '', ('id', 3), ('at', 116.84, 78.74, 0),
        #                          ('effects', ('font', ('size', 1.524, 1.524)))),
        #     ('pin', '1', ('uuid', '4eb52cb1-9134-412d-b80c-94785a2cfc61')),
        #     ('pin', '2', ('uuid', '15aa4aaa-9c23-451a-b015-db0e7f3f79c5'))
        #
        #     (property "Datasheet" "https://ngspice.sourceforge.io/docs/ngspice-html-manual/manual.xhtml#sec_Independent_Sources_for"
        #     (property "Description" "Voltage source, pulse"
        #     (property "Sim.Pins" "1=+ 2=-"
        #     (property "Sim.Type" "PULSE"
        #     (property "Sim.Device" "V"
        #     (property "Sim.Params" "y1=0 y2=1 td=2n tr=2n tf=2n tw=50n per=100n"

        _, d = self.to_dict(sexpr)
        self.fix_key_as_dict(d, 'property', 'properties')
        self.fix_key_as_dict(d, 'pin', 'pins')

        lib_id = d['lib_id']
        lib = self._symbol_libs[lib_id]
        properties = d['properties']
        symbol = Symbol(
            lib,
            *d['at'],
            mirror=d.get('mirror', None),
            unit=d['unit'],
            in_bom=d['in_bom'],
            on_board=d['on_board'],
            reference=self.sattr(properties['Reference']),
            value=self.sattr(properties['Value']),
            footprint=self.sattr(properties['Footprint']),
            datasheet=self.sattr(properties['Datasheet']),
            # simulation
            simulation_device=self.sattr(properties.get('Sim.Device', '')),
            simulation_type=self.sattr(properties.get('Sim.Type', '')),
            simulation_paramaters=self.sattr(properties.get('Sim.Params', '')),
            simulation_pins=self.sattr(properties.get('Sim.Pins', '')),
        )
        self._symbols.append(symbol)

    ##############################################

    def _make_netlist(self) -> None:
        # Find the ground
        ground = Net(0)
        for symbol in self._symbols:
            if symbol.lib_name in self.GROUND_SYMBOLS:
                self._logger.info(f"Symbol {symbol.reference} is ground")
                ground.link(symbol.first_pin)

        # Match on wire items
        for on_wire_items in (
                self._no_connections,
                self._labels,
                self._global_labels,
                self._hierarchical_labels,
        ):
            for _ in on_wire_items:
                _.match_wires(self._wires)

        # Match wires
        for wire1, wire2 in pairwise(self._wires):
            wire1.match_extremities(wire2)
        for junction in self._junctions:
            junction.match_wires(self._wires)

        # Assing a net to labels and assign wires recursively
        for label in self._labels:
            if label.name:
                label.make_net()
        # and to unassigned wires
        for wire in self._wires:
            if wire._net is None:  # note: .net check for None
                wire.net = Net()

        # Assign a net to pins
        for symbol in self._symbols:
            symbol.match_pin_with_wire(self._wires)
            symbol.match_pin_with_pin(self._symbols)

        # Check all wire have a net
        for _ in self._wires:
            if _._net is None:  # note: .net check for None
                raise NameError(f"Wire {_.id} is unassigned")

        # Assign remaining ids
        Net.assign_ids()

        # print('-'*100)
        # print("Nets")
        # for net in Net.NETS:
        #     print(net)
        #     ids = [_.id for _ in net._items if isinstance(_, Wire)]
        #     if ids:
        #         print(f"  wires={ids}")
        #     ids = [_.full_name for _ in net._items if isinstance(_, PinPosition)]
        #     if ids:
        #         print(f"  pins={ids}")
        # print()
        # print("Wires")
        # for wire in self._wires:
        #     print(f"Wire {wire.id} {wire.net}")
        # print('-'*100)

    ##############################################

    def dump_netlist(self) -> None:
        print(f"Number of nets: {Net.UUID}")
        for symbol in self._symbols:
            print(f"{symbol.reference} {symbol.value}")
            print(f"    @({symbol.x}, {symbol.y})  angle: {symbol.angle}")
            for pin in symbol.pins:
                net = str(pin.net)
                print(f"  p#{pin.number} {pin.name} -> {net: <30}   @({pin.x:.2f}, {pin.y:.2f})")
