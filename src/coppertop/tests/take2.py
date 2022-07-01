# **********************************************************************************************************************
#
#                             Copyright (c) 2021 David Briant. All rights reserved.
#
# **********************************************************************************************************************


import sys
if hasattr(sys, '_TRACE_IMPORTS') and sys._TRACE_IMPORTS: print(__name__)

from coppertop.pipe import *
from dm.core.types import txt, pydict, pylist


@coppertop(style=binary2)
def _take(d:pydict, ks: pylist) -> pydict:
    return {k:d[k] for k in ks}

@coppertop(style=binary2)
def _take(d:pydict, k:txt) -> pydict:
    return {k:d[k]}
