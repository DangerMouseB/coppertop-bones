# **********************************************************************************************************************
#
#                             Copyright (c) 2021 David Briant. All rights reserved.
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
sys._TRACE_IMPORTS = True
if hasattr(sys, '_TRACE_IMPORTS') and sys._TRACE_IMPORTS: print(__name__)

from coppertop.pipe import *
from coppertop.testing import assertRaises
from dm.core import check, each, tvseq
from ribs.types import txt, index, N
from bones.lang.metatypes import BTTuple
from coppertop.types import py



def test_anon():
    f = anon(index^index, lambda x: x + 1)
    fxs = tvseq((N ** index)[tvseq], [1, 2, 3]) >> each >> f
    fxs >> check >> typeOf >> (N ** index)[tvseq]
    with assertRaises(TypeError):
        fxs = tvseq((N ** index)[tvseq], [1, 2, 3]) >> each >> anon(txt ^ txt, lambda x: x + 1)

def test_partial():
    @coppertop
    def myunary_(a, b, c):
        return a + b + c
    t = myunary_ >> typeOf
    assert t == (BTTuple(py, py, py)^py)

    @coppertop
    def myunary(a:index, b:index, c:index) -> index:
        return a + b + c

    myunary >> check >> typeOf >> ((index*index*index)^index)
    myunary(1,_,3) >> check >> typeOf >> (index^index)

    fxs = tvseq((N ** index)[tvseq], [1, 2, 3]) >> each >> myunary(1,_,3)
    fxs >> check >> typeOf >> (N ** index)[tvseq]


def main():
    test_anon()
    test_partial()



if __name__ == '__main__':
    main()
    print('pass')

