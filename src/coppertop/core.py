# **********************************************************************************************************************
#
#                             Copyright (c) 2011-2021 David Briant. All rights reserved.
#
# **********************************************************************************************************************

version = '2022.03.06'       # coppertop.core.version


import sys
# sys._TRACE_IMPORTS = True
if hasattr(sys, '_TRACE_IMPORTS') and sys._TRACE_IMPORTS: print(__name__)


_all = set([
    'Missing', 'Null', 'Void', 'Err', 'getMyPublicMembers', 'getPublicMembersOf', 'CoppertopError', 'context',
    'ProgrammerError', 'NotYetImplemented'
])

import inspect


def getMyPublicMembers(moduleName, globals, locals):
    pass

def getPublicMembersOf(module):
    pass

def _getPublicMembersOnly(module):
    def _isInOrIsChildOf(name, names):
        for parentName in names:
            if name[0:len(parentName)] == parentName:
                return True
        return False
    names = [module.__name__]
    members = [(name, o) for (name, o) in inspect.getmembers(module) if (name[0:1] != '_')]         # remove private
    members = [(name, o) for (name, o) in members if not (inspect.isbuiltin(o) or inspect.ismodule(o))]   # remove built-ins and modules
    members = [(name, o) for (name, o) in members if not (isinstance(o, dict))]

    # this form is easier to debug than
    members2 = []
    for name, o in members:
        if _isInOrIsChildOf(o.__module__, names):
            members2.append((name, o))
    # this form - but this problem is tooling rather than inherently list comprehensions
    members = [
        (name, o)
            for (name, o) in members
                if _isInOrIsChildOf(o.__module__, names)        # keep all @coppertops and children
    ]
    return [name for (name, o) in members]

# the following are wrapped in exception handlers to make test driven development and debugging of coppertop easier

from ._singletons import CoppertopError, context

try:
    from bones.core.errors import *
    from bones.core import errors as _mod
    _all.update(_getPublicMembersOnly(_mod))
except Exception as ex:
    print(ex)
    pass

from bones.core.sentinels import Missing, Null, Void, Err

try:
    from ._module import *
    from . import _module as _mod
    _all.update(_getPublicMembersOnly(_mod))
except:
    pass

try:
    from ._repl import *
    from . import _repl as _mod
    _all.update(_getPublicMembersOnly(_mod))
except:
    pass


_all = list(_all)
_all.sort()
__all__ = _all


if hasattr(sys, '_TRACE_IMPORTS') and sys._TRACE_IMPORTS: print(__name__ + ' - done')
