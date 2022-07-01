# **********************************************************************************************************************
#
#                             Copyright (c) 2021 David Briant. All rights reserved.
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

