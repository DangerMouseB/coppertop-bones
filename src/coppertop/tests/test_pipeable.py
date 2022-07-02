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
if hasattr(sys, '_TRACE_IMPORTS') and sys._TRACE_IMPORTS: print(__name__)


from coppertop.pipe import *
from coppertop.core import *
from coppertop.testing import assertRaises
from bones.core.errors import NotYetImplemented
from bones.lang.metatypes import BTPrimitive
from dm.core import check, equal, fitsWithin, each
from dm.core import tvarray
from coppertop.tests.take1 import _take
from coppertop.tests.take2 import _take
from dm.core.types import index, pylist, litint

mat = BTPrimitive.ensure("mat2")
vec = BTPrimitive.ensure("vec2")


@coppertop(style=binary2)
def mmul(A:mat, B:vec) -> vec:
    answer = A @ B | vec
    return answer


def test_mmul():
    a = tvarray(mat, [[1, 2], [3, 4]])
    b = tvarray(vec, [1, 2])
    res = a >> mmul >> b
    res >> check >> typeOf >> vec


@coppertop(style=rau)
def unpack(f):
    return lambda xy: f(xy[0],xy[1])


def testTake():
    [1, 2, 3] >> _take >> 2 >> check >> equal >> [1, 2]
    [1, 2, 3] >> _take >> -2 >> check >> equal >> [2, 3]
    [1, 2, 3] >> _take >> (..., ...) >> check >> equal >> [1, 2, 3]
    [1, 2, 3] >> _take >> (1, ...) >> check >> equal >> [2, 3]
    [1, 2, 3] >> _take >> (..., 2) >> check >> equal >> [1, 2]
    [1, 2, 3] >> _take >> (0, 2) >> check >> equal >> [1, 2]

    {"a":1, "b":2, "c":3} >> _take >> "a" >> check >> equal >> {"a":1}
    {"a":1, "b":2, "c":3} >> _take >> ["a", "b"] >> check >> equal >> {"a":1, "b":2}


def testTypeOf():
    1 >> check >> typeOf >> litint
    1 >> typeOf >> check >> fitsWithin >> index


def testDoc():
    _take(pylist, index).d.__doc__ >> check >> equal >> 'hello'
    _take(pylist, pylist).d.__doc__ >> check >> equal >> 'there'


def test_rau():
    partiallyCalledBinary = ((1, 1), (2, 2), (3, 3)) >> each
    with assertRaises(NotYetImplemented):
        res = partiallyCalledBinary >> unpack >> (lambda x, y: x + y)
        res >> check >> equal >> [2, 4, 6]


def main():
    testTake()
    testTypeOf()
    testDoc()
    test_mmul()
    test_rau()


if __name__ == '__main__':
    main()
    print('pass')

