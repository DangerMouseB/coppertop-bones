# **********************************************************************************************************************
#
#                             Copyright (c) 2021 David Briant. All rights reserved.
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

