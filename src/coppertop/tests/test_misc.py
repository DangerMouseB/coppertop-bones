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



import sys, builtins
sys._TRACE_IMPORTS = True
if hasattr(sys, '_TRACE_IMPORTS') and sys._TRACE_IMPORTS: print(__name__)

from coppertop.pipe import *
from dm.core import check, equal, PP, each, interleave
from ribs.types import txt, index, num, bool

from coppertop.tests.int_adders import addOne, eachAddOne, eachAddTwo


@coppertop
def fred(a:index, b:txt, c:bool, d, e:num, f:num, g:txt+num) -> txt:
    return [a,b,c,d,e,f,g] >> each >> typeOf >> each >> builtins.str >> interleave >> ","
    # [a,b,c,d,e,f,g] each {e typeOf to(,<:txt>)} interleave ","

@coppertop
def addOneAgain(x: txt) -> txt:
    return x + 'One'

@coppertop
def addOneAgain(x):
    return x + 1

@coppertop
def addOneAgain(x):
    return x + 2



def test_redefine():
    1 >> addOneAgain >> check >> equal >> 3

def check_types_of_weak_things():
    fred(1 | index, "hello", True, (), 1, 1.3, 1.3 | num) >> check >> equal >> "index,txt,bool,pytuple,litint,litdec,num"


def main():
    test_redefine()
    check_types_of_weak_things()


if __name__ == '__main__':
    main()
    print('pass')

