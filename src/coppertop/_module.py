# **********************************************************************************************************************
#
#                             Copyright (c) 2011-2020 David Briant. All rights reserved.
#
# BSD 3-Clause License
#
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the
# following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this list of conditions and the
#    following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the
#    following disclaimer in the documentation and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its contributors may be used to endorse or promote
#    products derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES,
# INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY,
# WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
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
