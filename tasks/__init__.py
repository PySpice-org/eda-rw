####################################################################################################
#
# EDA-RW — Python library to read/write EDA Sexpr file format
# Copyright (C) 2019 Fabrice SALVAIRE
# SPDX-License-Identifier: AGPL-3.0-or-later
#
####################################################################################################

# http://www.pyinvoke.org

####################################################################################################

from invoke import Collection

####################################################################################################

# EDARW_SOURCE_PATH = Path(__file__).resolve().parent

####################################################################################################

# Fixme: better code

# from . import anaconda
from . import clean
# from . import doc
# from . import git
# from . import github
from . import stub
# from . import release
# from . import test

ns = Collection()
# ns.add_collection(Collection.from_module(anaconda))
ns.add_collection(Collection.from_module(clean))
# ns.add_collection(Collection.from_module(doc))
# ns.add_collection(Collection.from_module(git))
# ns.add_collection(Collection.from_module(github))
ns.add_collection(Collection.from_module(stub))
# ns.add_collection(Collection.from_module(release))
# ns.add_collection(Collection.from_module(test))
