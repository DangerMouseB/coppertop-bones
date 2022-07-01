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
from dm.core import check, equal
from ribs.types import txt, num

from coppertop.tests.int_adders import addOne, eachAddOne, eachAddTwo


# test that functions can be patched in a module more than once
@coppertop(patch='tests.adders')
def addTwo(x:txt) -> txt:
    return x + 'Two'

with context(halt=True):
    @coppertop(patch='tests.adders')
    def addTwo(x:txt) -> txt:
        return x + 'Two'


# test that functions can be redefined in "main"
with context(halt=True):
    @coppertop
    def fred():
        pass

with context(halt=True):
    @coppertop
    def fred():
        pass




def test_addOneEtc():
    1 >> addOne >> check >> equal >> 2
    [1, 2] >> eachAddOne >> check >> equal >> [2, 3]


def test_updatingAddOne():

    # now we want to use it with strings
    @coppertop
    def addOne(x:txt) -> txt:
        return x + 'One'

    # and floats
    @coppertop
    def addOne(x:num) -> num:
        return x + 1.0

    # check our new implementation
    1 >> addOne >> check >> equal >> 2
    'Two' >> addOne >> check >> equal >> 'TwoOne'
    1.0 >> addOne >> check >> equal >> 2.0

    # but
    with assertRaises(Exception) as ex:
        a = ['Two'] >> eachAddOne >> check >> equal >> ['TwoOne']
    # which is to be expected since the above are local (defined in a function)

    b = ['One'] >> eachAddTwo >> check >> equal >> ['OneTwo']


    with assertRaises(Exception) as ex:
        from coppertop.tests.int_adders2 import addOne



def main():
    test_addOneEtc()
    test_updatingAddOne()



if __name__ == '__main__':
    main()
    print('pass')

