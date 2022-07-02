# **********************************************************************************************************************
#
#                             Copyright (c) 2021-2022 David Briant. All rights reserved.
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

# a collection of usual types that aren't essential to the language
# in bones types can have constructors associated with them - so we have some classes embedded in the types module
# more for convenience and ease of understanding the module structure rather than anything deeper


import sys, builtins
if hasattr(sys, '_TRACE_IMPORTS') and sys._TRACE_IMPORTS: print(__name__)

from bones.lang.metatypes import BTPrimitive, BType, weaken
from bones.lang.types import *
import bones.lang.types


__all__ = bones.lang.types.__all__


i8 = BTPrimitive.define('i8').setExclusive
u8 = BTPrimitive.define('u8').setExclusive
i16 = BTPrimitive.define('i16').setExclusive
u16 = BTPrimitive.define('u16').setExclusive
i32 = BTPrimitive.define('i32').setExclusive
u32 = BTPrimitive.define('u32').setExclusive
i64 = BTPrimitive.define('i64').setExclusive
u64 = BTPrimitive.define('u64').setExclusive
f32 = BTPrimitive.define('f32').setExclusive
f64 = BTPrimitive.define('f64').setExclusive

__all__ += [
    'i8', 'u8', 'i16', 'u16', 'i32', 'u32', 'i64', 'u64', 'f32', 'f64',
]


# littxt is a python str and on assignment is notionally weakened to a ribs txt - in reality we just equate
# rib txt and python str
class BTxt(builtins.str):
    # (0 based)
    def __new__(cls, t, v, *args, **kwargs):
        return super(cls, cls).__new__(cls, v)
    @property
    def _t(self):
        return txt
    def _v(self):
        return self
    def __repr__(self):
        return f'{super().__repr__()}'
txt = BTPrimitive.define('txt').setExclusive.setCoercer(BTxt).setConstructor(BTxt)


# litbool is parsed in the SM to a storage format of a python bool and on assignment is notionally weakened to a
# rib bool - in reality we just equate rib bool and python bool
def _makeBool(t, v):
    return builtins.bool(v)
bool = BTPrimitive.define('bool').setExclusive.setCoercer(_makeBool).setConstructor(_makeBool)


# litfloat is parsed in the SM to a storage format of a python float and on assignment is notionally weakened to
# a rib num - in reality we just equate rib num and python float
class BNum(float):
    # (0 based)
    def __new__(cls, t, v, *args, **kwargs):
        return super(cls, cls).__new__(cls, v)

    @property
    def _t(self):
        return num

    def _v(self):
        return self

    def __repr__(self):
        return f'n{super().__repr__()}'

num = f64['num'].setCoercer(BNum)        # f64 is already exclusive


# litdate is parsed in the SM to a storage format of a python datetime.date and on assignment is notionally weakened
# to a rib date - in reality we just equate rub date and python datetime.date
date = BTPrimitive.define('date').setExclusive


# litint is parsed in the SM to a storage format of a python int and on assignment is notionally weakened to a
# rib index - in reality we just equate rib num and python float
class BIndex(int):
    # 1 based
    def __new__(cls, t, v, *args, **kwargs):
        return super(cls, cls).__new__(cls, v)
    @property
    def _t(self):
        return index
    def _v(self):
        return self
    def __repr__(self):
        return f'i{super().__repr__()}'
index = i64['index'].setCoercer(BIndex)         # i64 is already exclusive

__all__ += ['txt', 'bool', 'num', 'date', 'index']

for o in range(26):
    locals()['I'+chr(ord('a')+o)] = index
__all__ += [
    'index',
    'Ia', 'Ib', 'Ic', 'Id', 'Ie', 'If', 'Ig', 'Ih', 'Ii', 'Ij', 'Ik', 'Il', 'Im',
    'In', 'Io', 'Ip', 'Iq', 'Ir', 'Is', 'It', 'Iu', 'Iv', 'Iw', 'Ix', 'Iy', 'Iz'
]



N = BType('N')
for i in range(1, 11):
    t = N.ensure(BType(f'{i}'))
    locals()[t.name] = t
for o in range(26):
    t = N.ensure(BType(chr(ord('a')+o)))
    locals()[t.name] = t

__all__ += [
    'N',
    'N1', 'N2', 'N3', 'N4', 'N5', 'N6', 'N7', 'N8', 'N9', 'N10',
    'Na', 'Nb', 'Nc', 'Nd', 'Ne', 'Nf', 'Ng', 'Nh', 'Ni', 'Nj', 'Nk', 'Nl', 'Nm',
    'Nn', 'No', 'Np', 'Nq', 'Nr', 'Ns', 'Nt', 'Nu', 'Nv', 'Nw', 'Nx', 'Ny', 'Nz'
]



# classes for the underlying storage of count and offset in python - _t is hard-coded so they don't need additional
# boxing and also because python int cannot be subclassed with an additional variable

class BCount(int):
    # tv representing counts, natural numbers starting at 0
    def __new__(cls, t, v, *args, **kwargs):
        return super(cls, cls).__new__(cls, v)
    def __add__(self, other):
        return NotImplemented
    def __sub__(self, other):
        return NotImplemented
    def __mul__(self, other):
        return NotImplemented
    def __div__(self, other):
        return NotImplemented
    @property
    def _t(self):
        return count
    @property
    def _v(self):
        return self
    def __repr__(self):
        return f'c{super().__repr__()}'

count = i64['count'].setCoercer(BCount)
__all__ += ['count']


class BOffset(int):
    # (0 based)
    def __new__(cls, t, v, *args, **kwargs):
        return super(cls, cls).__new__(cls, v)
    @property
    def _t(self):
        return offset
    def _v(self):
        return self
    def __repr__(self):
        return f'o{super().__repr__()}'

offset = i64['offset'].setCoercer(BOffset)
for o in range(26):
    locals()['O'+chr(ord('a')+o)] = offset
__all__ += [
    'offset',
    'Oa', 'Ob', 'Oc', 'Od', 'Oe', 'Of', 'Og', 'Oh', 'Oi', 'Oj', 'Ok', 'Ol', 'Om',
    'On', 'Oo', 'Op', 'Oq', 'Or', 'Os', 'Ot', 'Ou', 'Ov', 'Ow', 'Ox', 'Oy', 'Oz'
]


class tvfloat(float):
    def __new__(cls, t, v, *args, **kwargs):
        instance = super(cls, cls).__new__(cls, v)
        instance._t_ = t
        return instance
    @property
    def _v(self):
        return super().__new__(float, self)
    @property
    def _t(self):
        return self._t_
    def __repr__(self):
        return f'{self._t}{super().__repr__()}'
    def _asT(self, t):
        self._t_ = t
        return self


__all__ += ['tvfloat']


class tvtxt(builtins.str):

    def __new__(cls, t, v, *args, **kwargs):
        t, v = 1, 2
        instance = super(cls, cls).__new__(cls, v)
        instance._t_ = t
        return instance

    @property
    def _v(self):
        return super().__new__(float, self)

    @property
    def _t(self):
        return self._t_

    def __repr__(self):
        return f'{self._t}{super().__repr__()}'

    def _asT(self, t):
        self._t_ = t
        return self


__all__ += ['tvtxt']



err = BTPrimitive.define('err')             # an error code of some sort
missing = BTPrimitive.define('missing')     # something that isn't there and should be there
null = BTPrimitive.define('null')           # the null set - something that isn't there and that's okay - the empty set

sys._Missing._t = missing
sys._NULL._t = null
sys._ERR._t = err
sys._VOID._t = void


__all__ += [
    'err', 'missing', 'null', 'void',
]


# could make +, -, / and * be type aware (index, offset, count should be orthogonal as well as exclusive)

weaken(litint, (index, offset, num, count))
weaken(litdec, (num,))
weaken(type(None), (null, void))
weaken(littxt, (txt,))


if hasattr(sys, '_TRACE_IMPORTS') and sys._TRACE_IMPORTS: print(__name__ + ' - done')
