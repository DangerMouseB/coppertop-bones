# **********************************************************************************************************************
#
#                             Copyright (c) 2011-2020 David Briant. All rights reserved.
#
# **********************************************************************************************************************

import sys
if hasattr(sys, '_TRACE_IMPORTS') and sys._TRACE_IMPORTS: print(__name__)


__all__ = ['ensurePath', 'printModules', 'unload']
from coppertop.pipe import *
from bones.core.sentinels import Void


@coppertop
def ensurePath(path):
    import sys
    if path not in sys.path:
        sys.path.insert(0, path)
    return Void


@coppertop
def printModules(root):
    noneNames = []
    moduleNames = []
    for k, v in sys.modules.items():
        if k.find(root) == 0:
            if v is None:
                noneNames.append(k)
            else:
                moduleNames.append(k)
    noneNames.sort()
    moduleNames.sort()
    print("****************** NONE ******************")
    for name in noneNames:
        print(name)
    print("****************** MODULES ******************")
    for name in moduleNames:
        print(name)
    return Void


@coppertop
def unload(module_name, leave_relative_imports_optimisation=False):
    # for description of relative imports optimisation in earlier versions of python see:
    # http://www.python.org/dev/peps/pep-0328/#relative-imports-and-indirection-entries-in-sys-modules

    l = len(module_name)
    module_names = list(sys.modules.keys())
    for name in module_names:
        if name[:l] == module_name:
            if leave_relative_imports_optimisation:
                if sys.modules[name] is not None:
                    del sys.modules[name]
            else:
                del sys.modules[name]
    return Void


if hasattr(sys, '_TRACE_IMPORTS') and sys._TRACE_IMPORTS: print(__name__ + ' - done')
