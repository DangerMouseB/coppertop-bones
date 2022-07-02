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

