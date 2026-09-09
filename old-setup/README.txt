.. -*- Mode: rst -*-

.. include:: project-links.txt
.. include:: abbreviation.txt

=================================================================
 EDA-RW : Python library to read/write EDA Sexpr file format 
=================================================================

|Pypi License|
|Pypi Python Version|

|Pypi Version|

..
   |Anaconda Version|
   |Anaconda Downloads|

   |KiCadRW Test Workflow|

**Quick Links**

* `Devel Branch <https://github.com/FabriceSalvaire/kicad-rw/tree/devel>`_
* `Production Branch <https://github.com/FabriceSalvaire/kicad-rw/tree/master>`_

..
   * `kicad-rw@conda-forge <https://github.com/conda-forge/kicad-rw-feedstock>`_
   * `conda-forge/kicad-rw <https://anaconda.org/conda-forge/kicad-rw>`_

Overview
========

What is KiCaD-RW ?
------------------

**A WORK IN PROGRESS...**

**keywords:** kicad, 6, sexpr, python, schema

**EDA-RW** is a Python module to read the KiCad version 6 schema file format (`.kicad_sch` file
extension) and to compute the netlist which is not actually stored by KiCad.  This module is
standalone and independent of the KiCad Python API, thus it don't require KiCad to work.

**Examples of use cases:**

* perform checks on circuit
* export a BOM
* generate a customised SPICE netlist, see `PySpice <https://github.com/FabriceSalvaire/PySpice>`_
* generate a `LaTeX/Tikz <https://ctan.org/pkg/pgf?lang=en>`_ graphic **TO BE IMPLEMENTED**
* generate a draft for `Circuit_macros <https://ece.uwaterloo.ca/~aplevich/Circuit_macros>`_,
  a tool for drawing electric high quality circuits, see `CircuitMacrosDumper`
* etc.

**EDA-RW** uses the Python library `sexpdata <https://github.com/jd-boyd/sexpdata>`_ to parse the file.

**How to go further:**

* KiCad uses Sexpr format, thus we don't have so many tools and a DTD like for XML
* We must use an external library to parse Sexpr format: sexpdata actually
* We must be able to parse the file without the need of KiCad, especially if we think KiCad is a reference EDA software
* We must not write tons of code to handle this format...
* We must try to auto-learn the KiCad format from a reference file collection and generate an OO API (fully automatic, jinja template)

`Look at this project <https://github.com/FabriceSalvaire/kicad-rw/projects/1>`_

`Comprehensive bibliography and relevant links on the topic <https://github.com/FabriceSalvaire/kicad-rw/blob/main/LINKS.md>`_

Where is the Documentation ?
----------------------------

*TO BE COMPLETED*

.. The documentation is available on the |KiCaDRWHomePage|_.

Where to get help or talk about KiCaD-RW ?
------------------------------------------

*TO BE COMPLETED*:

What are the main features ?
----------------------------

How to install it ?
-------------------

*TO BE COMPLETED*

.. Look at the `installation <https://kicad-rw.fabrice-salvaire.fr/releases/latest/installation.html>`_ section in the documentation.

Pull Request Recommendation
===========================

To make it easier to merge your pull request, you should divide your PR into smaller and easier-to-verify units.

Please do not make a pull requests with a lot of modifications which are difficult to check.

.. If I merge pull requests blindly then there is a high risk this software will become a mess quickly for everybody.

Credits
=======

Authors: `Fabrice Salvaire <http://fabrice-salvaire.fr>`_ and `contributors <https://github.com/FabriceSalvaire/kicad-rw/blob/master/CONTRIBUTORS.md>`_

News
====

.. include:: news.txt

.. End
