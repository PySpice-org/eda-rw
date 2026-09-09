#!/usr/bin/env python3

####################################################################################################
#
# EDA-RW — Python library to read/write EDA Sexpr file format
# Copyright (C) 2021 Fabrice SALVAIRE
# SPDX-License-Identifier: AGPL-3.0-or-later
#
####################################################################################################

# Forked from
#   source https://gitlab.com/kicad/libraries/kicad-library-utils/-/tree/master/symbol-generators/avr_da_db
#   PR     https://gitlab.com/kicad/libraries/kicad-symbols/-/merge_requests/3448
#   commit https://gitlab.com/kicad/libraries/kicad-library-utils/-/commit/5c6e9c4574ab7c7e56e23f6ed55518021814e005
#   author https://gitlab.com/jhol Joel Holdsworth

####################################################################################################

"""
This script generates symbols for the AVR-DA and AVD-DB series of
microcontrollers from Microchip.

The script uses CSV files derived from the "I/O Multiplexing" tables in the
Reference Manual PDFs.

Usage: python3 make_avr_dy.py > MCU_Microchip_AVR_Dx.kicad_sym
"""

####################################################################################################

from collections import namedtuple, deque
from pathlib import Path
import math
import re
import string

from pprint import pprint

####################################################################################################

from edarw.sexp import *

####################################################################################################

Device = namedtuple('Device', 'family flash_size pin_count sram_size')
devices = [
    Device('DA', 32, 28, 4),
    Device('DA', 32, 32, 4),
    Device('DA', 32, 48, 4),
    Device('DA', 64, 28, 8),
    Device('DA', 64, 32, 8),
    Device('DA', 64, 48, 8),
    Device('DA', 64, 64, 8),
    Device('DA', 128, 28, 16),
    Device('DA', 128, 32, 16),
    Device('DA', 128, 48, 16),
    Device('DA', 128, 64, 16),
    Device('DB', 32, 28, 4),
    Device('DB', 32, 32, 4),
    Device('DB', 32, 48, 4),
    Device('DB', 64, 28, 8),
    Device('DB', 64, 32, 8),
    Device('DB', 64, 48, 8),
    Device('DB', 64, 64, 8),
    Device('DB', 128, 28, 16),
    Device('DB', 128, 32, 16),
    Device('DB', 128, 48, 16),
    Device('DB', 128, 64, 16),
]

device_doc_dir = 'https://ww1.microchip.com/downloads/en/DeviceDoc/'
pdfs = {
    (32, 'DA'): 'AVR32DA28-32-48-Data-Sheet-40002228B.pdf',
    (64, 'DA'): 'AVR64DA28-32-48-64-Data-Sheet-40002233B.pdf',
    (128, 'DA'): 'AVR128DA28-32-48-64-DataSheet-DS40002183B.pdf',
    (32, 'DB'): 'AVR32DB28-32-48-DataSheet-DS40002301A.pdf',
    (64, 'DB'): 'AVR64DB28-32-48-64-DataSheet-DS40002300A.pdf',
    (128, 'DB'): 'AVR128DB28-32-48-64-DataSheet-DS40002247A.pdf',
}

families = sorted(set([_.family for _ in devices]))
family_descriptions = {'DA': 'Touch Sensing', 'DB': 'Op Amps and Multi-Voltage I/O'}

flash_sizes = sorted({_.flash_size for _ in devices})
pin_counts = sorted({_.pin_count for _ in devices})

max_freq = 24

packages = {
    28: ('SO', 'SP', 'SS'),
    32: ('PT', 'RXB'),
    48: ('PT', '6LX'),
    64: ('PT', 'MR'),
}

package_styles = {
    'MR': 'VQFN',
    '6LX': 'VQFN',
    'RXB': 'VQFN',
    'PT': 'TQFP',
    'SS': 'SSOP',
    'SO': 'SOIC',
    'SP': 'SPDIP',
}

Package = namedtuple('Package', 'style pin_count')
Footprint = namedtuple('Footprint', 'footprint footprint_filter')

footprints = {
    Package('SP', 28): Footprint('Package_DIP:DIP-28_W7.62mm', 'DIP*W7.62mm*'),
    Package('SO', 28): Footprint(
        'Package_SO:SOIC-28W_7.5x17.9mm_P1.27mm',
        'SOIC*7.5x17.9mm*P1.27mm*'
    ),
    Package('SS', 28): Footprint(
        'Package_SO:SSOP-28_5.3x10.2mm_P0.65mm',
        'SSOP*5.3x10.2mm*P0.65mm*'
    ),
    Package('RXB', 32): Footprint(
        'Package_DFN_QFN:QFN-32-1EP_5x5mm_P0.5mm_EP3.1x3.1mm',
        'QFN*1EP*5x5mm*P0.5mm*EP3.1x3.1mm*',
    ),
    Package('PT', 32): Footprint(
        'Package_QFP:TQFP-32_7x7mm_P0.8mm',
        'TQFP*7x7mm*P0.8mm*'
    ),
    Package('6LX', 48): Footprint(
        'Package_DFN_QFN:QFN-48-1EP_6x6mm_P0.4mm_EP4.2x4.2mm',
        'QFN*1EP*6x6mm*P0.4mm*EP4.2x4.2mm*',
    ),
    Package('PT', 48): Footprint(
        'Package_QFP:TQFP-48_7x7mm_P0.5mm',
        'TQFP*7x7mm*P0.5mm*'
    ),
    Package('MR', 64): Footprint(
        'Package_DFN_QFN:VQFN-64-1EP_9x9mm_P0.5mm_EP7.15x7.15mm',
        'VQFN*1EP*9x9mm*P0.5mm*EP7.15x7.15mm*',
    ),
    Package('PT', 64): Footprint(
        'Package_QFP:TQFP-64_10x10mm_P0.5mm',
        'TQFP*10x10mm*P0.5mm*'
    ),
}

####################################################################################################

grid = 2.54
width_padding = 6 * grid
height_padding = 2 * grid
pin_length = 1 * grid
font_width = 0.5 * grid
font_height = 0.5 * grid
text_offset = 0.5 * grid

####################################################################################################
#
# Read pins from CSV
#

Pin = namedtuple('Pin', 'number name special')

re_footnote = re.compile(r'\([0-9]+\)')

def load_pins(family, flash_size, pin_count, package):
    def parse_line(line):
        cells = line.split(',')
        pin_num = cells[package_col]
        special = cells[special_col]
        if pin_num:
            return Pin(
                int(pin_num),
                re_footnote.sub('', cells[pin_name_col]),
                None if special == '' else special,
            )
        return None

    filename_pattern = f'avr{flash_size}{family.lower()}-io-mux.csv'
    path = Path(__file__).parent.joinpath('data', filename_pattern)
    with open(path, 'rt') as fh:
        heading_cells = fh.readline().rstrip().split(',')
        for i, col_name in enumerate(heading_cells):
            if f'{package}{pin_count}' in col_name.split('/'):
                package_col = i
        pin_name_col = heading_cells.index('Pin Name')
        special_col = heading_cells.index('Special')
        return [pin for pin in (parse_line(line) for line in fh) if pin]

####################################################################################################

PinBanks = namedtuple('PinBanks', 'power ground misc ports')
Port = namedtuple('Port', 'letter pins')

def bank_pins(pins):
    def filter_port_pins(port):
        port_name = 'P' + port
        return [pin for pin in pins if pin.name.startswith(port_name)]

    banks = PinBanks(
        [pin for pin in pins if 'VDD' in pin.name],
        [pin for pin in pins if 'GND' in pin.name],
        [pin for pin in pins if pin.name in ('UPDI',)],
        [
            p
            for p in (
                Port(letter, filter_port_pins(letter))
                for letter in string.ascii_uppercase
            )
            if p.pins
        ],
    )

    # Check for remaining pins
    remaining_pins = set(pins) - set(banks.power) - set(banks.ground) - set(banks.misc)
    for port in banks.ports:
        remaining_pins -= set(port.pins)
    if remaining_pins:
        remaining_pins = sorted(remaining_pins, key=lambda p: p.number)
        raise ValueError(
            'Some pins were not sorted into banks: ' +
            ', '.join(f'{p.number}:{p.name}' for p in remaining_pins)
        )

    return banks

####################################################################################################

def get_part_name(family, device, package):
    return f'AVR{device.flash_size}{family}{device.pin_count}x-x{package}'

####################################################################################################

def has_exposed_pad(pin_count, package):
    return '-1EP' in footprints[Package(package, pin_count)].footprint

####################################################################################################

def make_properties(family, device, package, width, height, value_offset):
    package_style = package_styles[package]
    footprint = footprints[Package(package, device.pin_count)]
    package_name = f'{package_style}-{device.pin_count}'
    part_name = get_part_name(family, device, package)

    description = (
        f'{max_freq}MHz, {device.flash_size}kB Flash, {device.sram_size}kB SRAM, EEPROM '
        f'with {family_descriptions[family]}, {package_name}'
    )
    datasheet = device_doc_dir + pdfs[(device.flash_size, family)]

    return [
        (PROPERTY, "Reference", "U", (ID, 0), (AT, -width/2, height/2 + text_offset, 0),
         (EFFECTS, (FONT, (SIZE, font_width, font_height)), (JUSTIFY, LEFT, BOTTOM)),
         ),
        (PROPERTY, "Value", part_name, (ID, 1), (AT, value_offset, -height/2 - text_offset, 0),
         (EFFECTS, (FONT, (SIZE, font_width, font_height)), (JUSTIFY, LEFT, TOP)),
         ),
        (PROPERTY, "Footprint", footprint.footprint, (ID, 2), (AT, 0, 0, 0),
         (EFFECTS, (FONT, (SIZE, font_width, font_height), ITALIC), HIDE),
         ),
        (PROPERTY, "Datasheet", datasheet, (ID, 3), (AT, 0, 0, 0),
         (EFFECTS, (FONT, (SIZE, font_width, font_height)), HIDE),
         ),
        (PROPERTY, "ki_keywords", f"AVR 8bit Microcontroller AVR-{family}", (ID, 4), (AT, 0, 0, 0),
         (EFFECTS, (FONT, (SIZE, font_width, font_height)), HIDE),
         ),
        (PROPERTY, "ki_description", description, (ID, 5), (AT, 0, 0, 0),
         (EFFECTS, (FONT, (SIZE, font_width, font_height)), HIDE),
         ),
        (PROPERTY, "ki_fp_filters", footprint.footprint_filter, (ID, 6), (AT, 0, 0, 0),
         (EFFECTS, (FONT, (SIZE, font_width, font_height)), HIDE),
         ),
    ]

####################################################################################################

BaseInfo = namedtuple('BaseInfo', 'name width height value_offset')

def make_base_device(family, device, package):
    # print()
    # print('make_base_device', family, device, package)
    part_name = get_part_name(family, device, package)
    package_style = package_styles[package]

    banks = bank_pins(
        load_pins(family, device.flash_size, device.pin_count, package_style)
    )

    # for bank in ('power', 'ground', 'misc'):
    #     print(f'- {bank}')
    #     for pin in getattr(banks, bank):
    #         print(' ', pin)
    # for port in banks.ports:
    #     print(f'- {port.letter}')
    #     for pin in port.pins:
    #         print(' ', pin)
        
    left_banks = []
    right_banks = []
    side_banks = deque([port.pins for port in banks.ports] + [banks.misc])

    def side_width(bank):
        return len(banks.ground) - 1

    def side_height(banks):
        if len(banks) == 0:
            return 0
        return sum((len(bank) + 1 for bank in banks), 0) - 2

    # Fixme: side_width return for ground !
    top_side_width = side_width(banks.power)
    bottom_side_width = side_width(banks.ground)
    inner_width = math.ceil(max(top_side_width, bottom_side_width) / 2) * 2 * grid
    outline_width = inner_width + width_padding * 2

    # dispatch ports on right and left side
    #   try to get the same number of pins on both side
    while side_banks:
        if side_height(left_banks) >= side_height(right_banks):
            right_banks.append(side_banks.popleft())
        else:
            left_banks.append(side_banks.pop())

    # Fixme: duplicate code
    inner_height = math.ceil(max(side_height(left_banks), side_height(right_banks)) / 2) * 2 * grid
    outline_height = inner_height + height_padding * 2

    left = -outline_width / 2
    right = -left
    top = outline_height / 2
    bottom = -top

    sexp_part = [SYMBOL, part_name, (IN_BOM, YES), (ON_BOARD, YES)]

    # Properties
    value_offset = (bottom_side_width // 2 + 1) * grid
    sexp_part += make_properties(family, device, package, outline_width, outline_height, value_offset)

    # Background
    _ = (SYMBOL, f'{part_name}_0_1',
         (RECTANGLE, (START, left, top), (END, right, bottom),
          (STROKE, (WIDTH, 0.254), (TYPE, DEFAULT), (COLOR, 0, 0, 0, 0)),
          (FILL, (TYPE, BACKGROUND)),
          )
         )
    sexp_part.append(_)

    # Pins
    sexp_pins = [SYMBOL, f'{part_name}_1_1']
    sexp_part.append(sexp_pins)

    def make_pin_label(pin):
        if pin.special == 'RESET':
            return '~{RESET}/' + pin.name
        elif pin.special is not None and pin.special not in (
            'CLKOUT',
            'EXTCLK',
            'TWI',
            'TWI Fm+',
            'UPDI',
        ):
            special = pin.special
            if special == 'XTALHF1 EXTCLK':
                special = 'XTALHF1'
            return f'{special}/{pin.name}'
        return pin.name

    def directionality(pin):
        if pin.name in ('UPDI',):
            return 'input'
        return 'bidirectional'

    def render_pin(type_, name, number, x, y, angle, hide=False):
        sexp = [PIN, Symbol(type_), LINE, (AT, x, y, angle), (LENGTH, pin_length)]
        if hide:
            sexp.append(HIDE)
        sexp += [
            (NAME, name, (EFFECTS, (FONT, (SIZE, font_width, font_height)))),
            (NUMBER, str(number), (EFFECTS, (FONT, (SIZE, font_width, font_height)))),
        ]
        return sexp

    def render_side_banks(banks, x, angle):
        y = inner_height / 2
        for bank in banks:
            for pin in bank:
                _ = render_pin(directionality(pin), make_pin_label(pin), pin.number, x, y, angle)
                nonlocal sexp_pins
                sexp_pins.append(_)
                y -= grid
            y -= grid

    def render_power_bank(pins, y, angle):
        def render_power_pin(name, number, stacked=False):
            nonlocal sexp_pins
            _ = render_pin(
                'passive' if stacked else 'power_in',
                name, number, x, y, angle, hide=stacked,
            )
            nonlocal sexp_pins
            sexp_pins.append(_)
        pin_stacks = {}
        for p in pins:
            pin_stacks.setdefault(p.name, [])
            pin_stacks[p.name].append(p.number)
        x = -(len(pin_stacks) // 2) * grid
        for pin_name in sorted(pin_stacks):
            pin_numbers = sorted(pin_stacks[pin_name])
            render_power_pin(pin_name, pin_numbers[0])
            for pin_number in pin_numbers[1:]:
                render_power_pin(pin_name, pin_number, stacked=True)
            x += grid

    render_side_banks(right_banks, right + pin_length, 180)
    render_side_banks(left_banks, left - pin_length, 0)
    render_power_bank(banks.power, top + pin_length, 270)

    ground_pins = banks.ground
    if has_exposed_pad(device.pin_count, package):
        ground_pins.append(Pin(device.pin_count + 1, 'GND', ''))
    render_power_bank(ground_pins, bottom - pin_length, 90)

    base_info = BaseInfo(part_name, outline_width, outline_height, value_offset)

    return base_info, sexp_part

####################################################################################################

def make_alias_device(family, device, package, base_info):
    part_name = get_part_name(family, device, package)
    sexp = [SYMBOL, part_name, (EXTENDS, base_info.name)]
    sexp += make_properties(
        family,
        device,
        package,
        base_info.width,
        base_info.height,
        base_info.value_offset,
    )
    return sexp

####################################################################################################

def main():
    sexp_root = [
        KICAD_SYMBOL_LIB,
        (VERSION, Symbol('20211014')),
        (GENERATOR, Symbol('kicad_symbol_editor')),
    ]

    for family in families:
        for pin_count in pin_counts:
            family_devices_with_pin_count = [d for d in devices if d.family == family and d.pin_count == pin_count]
            # base device has the smallest flash size
            base_device = family_devices_with_pin_count[0]

            packages_with_pin_count = packages[pin_count]

            # Process no exposed pad
            packages_with_no_exposed_pad = [p for p in packages_with_pin_count if not has_exposed_pad(pin_count, p)]
            base_package_with_no_exposed_pad = (
                packages_with_no_exposed_pad[0]
                if packages_with_no_exposed_pad
                else None
            )
            if base_package_with_no_exposed_pad:
                base_with_no_exposed_pad_info, sexp = make_base_device(family, base_device, base_package_with_no_exposed_pad)
                sexp_root.append(sexp)
            else:
                base_with_no_exposed_pad_info = None
            for alias_device in family_devices_with_pin_count:
                for package in packages_with_no_exposed_pad:
                    if (
                        alias_device != base_device
                        or package != base_package_with_no_exposed_pad
                    ):
                        _ = make_alias_device(family, alias_device, package, base_with_no_exposed_pad_info)
                        sexp_root.append(_)

            # Process with exposed pad
            packages_with_exposed_pad = [p for p in packages_with_pin_count if has_exposed_pad(pin_count, p)]
            base_package_with_exposed_pad = (
                packages_with_exposed_pad[0]
                if packages_with_exposed_pad
                else None
            )
            if base_package_with_exposed_pad:
                base_with_exposed_pad_info, sexp = make_base_device(family, base_device, base_package_with_exposed_pad)
                sexp_root.append(sexp)
            else:
                base_with_exposed_pad_info = None
            for alias_device in family_devices_with_pin_count:
                for package in packages_with_exposed_pad:
                    if (
                        alias_device != base_device
                        or package != base_package_with_exposed_pad
                    ):
                        _ = make_alias_device(family, alias_device, package, base_with_exposed_pad_info)
                        sexp_root.append(_)

    return sexp_root

####################################################################################################

if __name__ == '__main__':
    sexp = main()
    sexp_str = dumps(sexp)
    with open('out', 'w') as fh:
        fh.write(sexp_str)
