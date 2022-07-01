# **********************************************************************************************************************
#
#                             Copyright (c) 2021 David Briant. All rights reserved.
#
# **********************************************************************************************************************

BONES_MODULE = 'tests.adders'

from coppertop.pipe import *
from ribs.types import index, pylist

# this will throw an error if imported after int_adders.py
@coppertop
def addOne(x:index) -> index:
    return x + 1
