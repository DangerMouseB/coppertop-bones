# **********************************************************************************************************************
#
#                             Copyright (c) 2017-2020 David Briant. All rights reserved.
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


from copy import copy as _copy


_list_iter_type = type(iter([]))
_numpy = None        # don't import numpy proactively


class _callFReturnX(object):
    def __init__(self, f2, pp):
        self.f2 = f2
        self.f1 = lambda x:x
        self.pp = pp
    def __rrshift__(self, lhs):   # lhs >> self
        "ENT"
        self.f2(self.f1(lhs))
        self.f1 = lambda x: x
        return lhs
    def __call__(self, f1):
        "ENT"
        self.f1 = f1
        return self
    def __lshift__(self, rhs):    # self << rhs
        "ENT"
        self.f2(self.f1(rhs))
        self.f1 = lambda x: x
        return self
    def __repr__(self):
        return self.pp


def _printRepr(x):
    print(repr(x))
RR = _callFReturnX(_printRepr, 'RR')

def _printDir(x):
    print(dir(x))
DD = _callFReturnX(_printDir, 'DD')

def _printHelp(x):
    if hasattr(x, '_doc'):
        print(x._doc)
    else:
        help(x)
HH = _callFReturnX(_printHelp, 'HH')

def _printType(x):
    print(type(x))
TT = _callFReturnX(_printType, 'TT')

def _isNdArray(x):
    global _numpy
    if type(x).__name__ != "ndarray":
        return False
    try:
        import numpy as _numpy
        return isinstance(x, _numpy.ndarray)
    except (ModuleNotFoundError, AttributeError):      # cf None.ndarray if numpy is not installed
        return False

def _printLen(x):
    if isinstance(x, _list_iter_type):
        x = list(_copy(x))
    if _isNdArray(x):
        print(x.shape)
    else:
        print(len(x))

LL = _callFReturnX(_printLen, 'LL')



if hasattr(sys, '_TRACE_IMPORTS') and sys._TRACE_IMPORTS: print(__name__ + ' - done')
