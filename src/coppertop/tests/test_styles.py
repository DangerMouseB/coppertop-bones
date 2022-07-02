# **********************************************************************************************************************
#
#                             Copyright (c) 2020-2021 David Briant. All rights reserved.
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


from coppertop.core import CoppertopError
from coppertop.pipe import *
from coppertop.testing import assertRaises
from dm.core import _, check, equal


def prettyArgs(*args):
    return ', '.join([str(arg) for arg in args])


@coppertop(style=nullary)
def nullary0():
    return 'nullary0'

@coppertop(style=nullary)
def nullary1(a):
    return f'nullary1({prettyArgs(a)})'

@coppertop(style=nullary)
def nullary2(a, b):
    return f'nullary2({prettyArgs(a, b)})'

@coppertop
def unary1(a):
    return f'unary1({prettyArgs(a)})'

@coppertop
def unary2(a, b):
    return f'unary2({prettyArgs(a, b)})'

@coppertop
def unary3(a, b, c):
    return f'unary3({prettyArgs(a, b, c)})'

@coppertop(style=rau)
def rau1(a):
    return f'rau1({prettyArgs(a)})'

@coppertop(style=rau)
def rau2(a, b):
    return f'rau2({prettyArgs(a, b)})'

@coppertop(style=rau)
def rau3(a, b, c):
    return f'rau3({prettyArgs(a, b, c)})'

@coppertop(style=binary)
def binary2(a, b):
    return f'binary2({prettyArgs(a, b)})'

@coppertop(style=binary)
def binary3(a, b, c):
    return f'binary3({prettyArgs(a, b, c)})'

@coppertop(style=ternary)
def ternary3(a, b, c):
    return f'ternary3({prettyArgs(a, b, c)})'



def testNullary():
    str(nullary1(1)) >> check >> equal >> 'nullary1(1)'
    str(nullary2(1, _)) >> check >> equal >> 'nullary2(1, TBI{})'
    str(nullary2(1, _)(2)) >> check >> equal >> 'nullary2(1, 2)'

    with assertRaises(CoppertopError) as e:
        nullary1(_)(1, 2)
    e.exceptionValue.args[0] >> check >> equal >> 'nullary1 - too many args - got 2 needed 1'

    with assertRaises(CoppertopError) as e:
        2 >> nullary2(1, _)
    e.exceptionValue.args[0] >> check >> equal >> 'syntax not of form nullary()'


def testUnary():
    str(unary1(1)) >> check >> equal >> 'unary1(1)'
    str(unary2(1, _)) >> check >> equal >> 'unary2(1, TBI{})'
    str(2 >> unary2(1, _)) >> check >> equal >> 'unary2(1, 2)'

    with assertRaises(CoppertopError) as e:
        unary1(_)(1, 2)
    e.exceptionValue.args[0] >> check >> equal >> 'unary1 - too many args - got 2 needed 1'

    with assertRaises(CoppertopError) as e:
        2 >> unary3(1, _, _)
    e.exceptionValue.args[0] >> check >> equal >> 'unary3 needs 2 args but 1 will be piped'

    str(nullary1(1) >> unary1) >> check >> equal >> 'unary1(nullary1(1))'


def testRau():
    str(rau1(1)) >> check >> equal >> 'rau1(1)'
    str(rau2(1, _)) >> check >> equal >> 'rau2(1, TBI{})'
    str(rau2(1, _) >> 2) >> check >> equal >> 'rau2(1, 2)'

    with assertRaises(CoppertopError) as e:
        rau1(_)(1, 2)
    e.exceptionValue.args[0] >> check >> equal >> 'rau1 - too many args - got 2 needed 1'

    with assertRaises(CoppertopError) as e:
        rau3(1, _, _) >> 2
    e.exceptionValue.args[0] >> check >> equal >> 'needs 2 args but 1 will be piped'

    str(rau1 >> 1) >> check >> equal >> 'rau1(1)'
    str(rau1 >> nullary1(1)) >> check >> equal >> 'rau1(nullary1(1))'

    with assertRaises(TypeError) as e:
        rau1 >> unary1
    with assertRaises(TypeError) as e:
        rau1 >> binary2
    with assertRaises(TypeError) as e:
        rau1 >> ternary3



def testBinary():
    # in python we can't stop partial binding of binaries as we don't have access to the parser
    str(binary2(1, 2)) >> check >> equal >> 'binary2(1, 2)'
    str(1 >> binary3(_, 2, _)) >> check >> equal >> 'binary3(1, 2, TBI{})'
    str(1 >> binary3(_, 2, _) >> 3) >> check >> equal >> 'binary3(1, 2, 3)'
    str(1 >> binary2 >> 2) >> check >> equal >> 'binary2(1, 2)'
    str(1 >> binary2 >> unary1) >> check >> equal >> 'binary2(1, unary1)'



def testTernary():
    # consider the following - it shows that rau, binary, ternary overwrite any function as args r1 or r2
    str([1, 2] >> ternary3 >> binary2 >> [3, 4]) >> check >> equal >> 'ternary3([1, 2], binary2, [3, 4])'
    str([1, 2] >> ternary3 >> binary3(_, 2, _) >> [3, 4]) >> check >> equal >> 'ternary3([1, 2], binary3(TBI{}, 2, TBI{}), [3, 4])'



# def testExamples():
#     join = MultiFunction('join', Binary)
#     mul = MultiFunction('mul', Binary)
#     add = MultiFunction('add', Binary)
#     fred = MultiFunction('fred', Unary)
#     eachBoth = MultiFunction('eachBoth', Ternary)
#     each = MultiFunction('each', Binary)
#     inject = MultiFunction('inject', Binary)
#
#     str([1, 2] >> each >> fred) >> check >> equal >> 'each([1, 2], fred)'
#     str([1, 2] >> join >> mul >> fred) >> check >> equal >> 'fred(join([1, 2], mul))'
#     str([1, 2] >> inject(_, 0, _) >> add) >> check >> equal >> 'inject([1, 2], 0, add)'
#     str([1, 2] >> eachBoth >> mul >> [2, 4] >> fred) >> check >> equal >> 'fred(eachBoth([1, 2], mul, [2, 4]))'
#
#     with assertRaises(CoppertopError) as e:
#         [1, 2] >> each(_, fred)
#     e.exceptionValue.args[0] >> check >> equal >> 'needs 1 args but 2 will be piped'



def main():
    testNullary()
    testUnary()
    testRau()
    testBinary()
    testTernary()
    # testExamples()


if __name__ == '__main__':
    main()
    print('pass')


