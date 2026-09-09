# EDA-RW : a Python library to read/write EDA Sexpr file format

[![KiCadRW
license](https://img.shields.io/pypi/l/KiCadRW.svg)](https://pypi.python.org/pypi/KiCadRW)
[![KiCadRW python
version](https://img.shields.io/pypi/pyversions/KiCadRW.svg)](https://pypi.python.org/pypi/KiCadRW)

[![KiCadRW last
version](https://img.shields.io/pypi/v/KiCadRW.svg)](https://pypi.python.org/pypi/KiCadRW)

**Quick Links**

  - [Devel Branch](https://github.com/FabriceSalvaire/kicad-rw/tree/devel)
  - [Production Branch](https://github.com/FabriceSalvaire/kicad-rw/tree/master)

## Overview

### What is EDA-RW ?

**EDA-RW** is a Python module to read/write the [KiCad](https://www.kicad.org) version 6 schema file
format (<span class="title-ref">.kicad\_sch</span> file extension) and
[LibrePCB](https://librepcb.org) project files.

For KiCad, it can compute the netlist which is not actually stored. Notice, this module is
standalone and independent of the KiCad Python API, thus it don't require KiCad to work.

**Examples of use cases:**
- generate a customised SPICE netlist, see [PySpice](https://github.com/PySpice-org/PySpice)
- automate the creation of KiCad symbols 
- perform checks on circuit (ERC)
- export a BOM
- generate a draft for [Circuit\_macros](https://ece.uwaterloo.ca/~aplevich/Circuit_macros), a
  tool for drawing electric high quality circuits, see
  <span class="title-ref">CircuitMacrosDumper</span>
- generate a [LaTeX/Tikz](https://ctan.org/pkg/pgf?lang=en) graphic **TO BE IMPLEMENTED**
- etc.

**EDA-RW** uses the Python library [sexpdata](https://github.com/jd-boyd/sexpdata) to parse this
file format.

### Where is the Documentation ?

*TO BE COMPLETED*

### Where to get help or talk about EDA-RW ?

*TO BE COMPLETED*:

### What are the main features ?

### How to install it ?

Use [uv](https://docs.astral.sh/uv) !

## Pull Request Recommendation

To make it easier to merge your pull request, you should divide your PR into smaller and
easier-to-verify units.

Please do not make a pull requests with a lot of modifications which are difficult to check.

## Credits

Authors: [Fabrice Salvaire](http://fabrice-salvaire.fr) and
[contributors](https://github.com/FabriceSalvaire/kicad-rw/blob/master/CONTRIBUTORS.md)

## News

### 2026-09

In 2026, the [LibrePCB](https://librepcb.org) schematic editor is a true alternative to KiCad to
draw a circuit for simulation (not for complex PCB).  Moreover, LibrePCB features a real advantage
in comparison to KiCad, since it stores the circuit (netlist).  As opposite, KiCad stores a drawing
similar to SVG but using the Sexpr file format.  Thus we don't need the infamous code to perform a
kind of OCR for EDA... Well, I guess it is due to a historical reason ??? But, WTF, it is the EDA
conerstone !

Thanks, to modern Python and annotations, I was able to write an efficient code to read the LibrePCB
format.

Now, the code is fully annotated and checked by the great pair of Python checkers
[Ty](https://docs.astral.sh/ty)+[Ruff](https://docs.astral.sh/ruff) which greatly improve my Emacs
coding experience and the code quality.

### 2021-05

This project was started on 2021-05-21 in order to provide a way to read a netlist from a KiCad
schema for [PySpice](https://github.com/PySpice-org/pyspice).  Indeed it is quite cumbersome to
write manually a Spice netlist, thus the possibility to draw the circuit using a GUI and then export
it to PySpice is a real game changer.  A second motivation was to automate the creation of symbols
for KiCad.

# How to go further ?

- KiCad uses Sexpr format, thus we don't have so many tools and a DTD like for XML
- We must use an external library to parse Sexpr format: sexpdata actually
- We must be able to parse the file without the need of KiCad, especially if we think KiCad is a
  reference EDA software
- We must not write tons of code to handle this format...
- We must try to auto-learn the KiCad format from a reference file collection and generate an OO
  API (fully automatic, jinja template)

- [Look at this project](https://github.com/FabriceSalvaire/kicad-rw/projects/1)
- [Some comprehensive bibliography and relevant links on the
topic](https://github.com/FabriceSalvaire/kicad-rw/blob/main/LINKS.md)
