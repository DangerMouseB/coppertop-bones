# **********************************************************************************************************************
#
#                             Copyright (c) 2011-2021 David Briant. All rights reserved.
#
# **********************************************************************************************************************

import sys
if hasattr(sys, '_TRACE_IMPORTS') and sys._TRACE_IMPORTS: print(__name__)


__all__ = [
    'noun', 'nullary', 'unary', 'binary', 'ternary', 'rau',
    'TBI', 'void',
    'litint', 'litdec', 'littxt', 'litsym', 'litsyms', 'litdate',
    'opaque'
]
from bones.lang.metatypes import BTPrimitive, BType, BTTuple

noun = BTPrimitive.define("noun")
nullary = BTPrimitive.define("nullary")
unary = BTPrimitive.define("unary")
binary = BTPrimitive.define("binary")
ternary = BTPrimitive.define("ternary")
rau = BTPrimitive.define("rau")

TBI = BTPrimitive.define("TBI").setExclusive
void = BTPrimitive.define('void').setExclusive   # something that isn't there and shouldn't be there
nulltuple = BTTuple()

# types used in parser
litint = BTPrimitive.define('litint').setExclusive
litdec = BTPrimitive.define('litdec').setExclusive
littxt = BTPrimitive.define('littxt').setExclusive
litsym = BTPrimitive.define('litsym').setExclusive
litsyms = BTPrimitive.define('litsyms').setExclusive
litdate = BTPrimitive.define('litdate').setExclusive

# a type of known fized size (in bytes) that bones treats as a memory value - could be a void*
# allows fully typed aggregation operations to be implemented - e.g. N**voidstar(8)
opaque = BTPrimitive.define('opaque').setExclusive


# expose a bunch of schema variables - code can get more via schemaVariableForOrd
T = BType('T')
for i in range(1, 21):
    t = BType(f'T{i}')
    locals()[t.name] = t
for o in range(26):
    t = BType(f"T{chr(ord('a') + o)}")
    locals()[t.name] = t

__all__ += [
    'T',
    'T1', 'T2', 'T3', 'T4', 'T5', 'T6', 'T7', 'T8', 'T9', 'T10',
    'T11', 'T12', 'T13', 'T14', 'T15', 'T16', 'T17', 'T18', 'T19', 'T20',
    'Ta', 'Tb', 'Tc', 'Td', 'Te', 'Tf', 'Tg', 'Th', 'Ti', 'Tj', 'Tk', 'Tl', 'Tm',
    'Tn', 'To', 'Tp', 'Tq', 'Tr', 'Ts', 'Tt', 'Tu', 'Tv', 'Tw', 'Tx', 'Ty', 'Tz'
]
