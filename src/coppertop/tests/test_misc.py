# **********************************************************************************************************************
#
#                             Copyright (c) 2021 David Briant. All rights reserved.
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

