# **********************************************************************************************************************
#
#                             Copyright (c) 2021 David Briant. All rights reserved.
#
# **********************************************************************************************************************



import sys
sys._TRACE_IMPORTS = True
if hasattr(sys, '_TRACE_IMPORTS') and sys._TRACE_IMPORTS: print(__name__)

from ctypes import c_long

from coppertop.core import *
from coppertop.testing import assertRaises
from coppertop._singletons import _CoWProxy, _Scope
from dm.core import check, equal, tvstruct, PP




def numRefs(x):
    if isinstance(x, _CoWProxy):
        return c_long.from_address(id(x._target)).value - 1
    else:
        return c_long.from_address(id(x)).value



def test_scope():
    _ = _Scope()

    with assertRaises(AttributeError):
        _.fred

    _.fred = []
    with assertRaises(IndexError):
        _.fred[0]

    _.joe = {}
    with assertRaises(KeyError):
        _.joe['a']

    class Sally(object):pass
    _.sally = Sally()
    with assertRaises(AttributeError):
        _.sally.a


def test_iters():
    _ = _Scope()
    _.fred = {'a':1}

    ks = []
    with context(print=True):
        for k in _.fred:
            ks.append(k)
    assert ks == ['a']

    ks = []
    with context(print=True):
        for k in _.fred.keys():
            ks.append(k)
    assert ks == ['a']

    ks = []
    with context(print=True):
        for k in _.fred.values():
            ks.append(k)
    assert ks == [1]

    ks = []
    with context(print=True):
        for k in _.fred.items():
            ks.append(k)
    assert ks == [('a',1)]


def test_cow():
    _ = _Scope()

    "\n_.pad = map(a=map({1:'a1'})" >> PP
    _.pad = {'a': {1:'a1'}}
    f"_.pad => {_.pad}" >> PP
    f"  _.pad -> {numRefs(_.pad)}" >> PP
    f"  _.pad -> {numRefs(_.pad)}" >> PP
    f"  _.pad[\'a\'] -> {numRefs(_.pad['a'])}" >> PP
    f"  _.pad[\'a\'][1] -> {numRefs(_.pad['a'][1])}" >> PP

    "\n_.fred = _.pad['a']" >> PP
    _.fred = _.pad['a']
    f"_.pad => {_.pad}" >> PP
    f"_.fred => {_.fred}" >> PP
    f"  _.pad -> {numRefs(_.pad)}" >> PP
    f"  _.pad[\'a\'] -> {numRefs(_.pad['a'])}" >> PP
    f"  _.pad[\'a\'][1] -> {numRefs(_.pad['a'][1])}" >> PP
    f"  _.fred -> {numRefs(_.fred)}" >> PP

    "\n_.pad[\'b\'] = {1:'b1'}" >> PP
    _.pad['b'] = {1:'b1'}
    f"_.pad => {_.pad}" >> PP
    f"_.fred => {_.fred}" >> PP
    f"  _.pad -> {numRefs(_.pad)}" >> PP
    f"  _.pad[\'a\'] -> {numRefs(_.pad['a'])}" >> PP
    f"  _.pad[\'a\'][1] -> {numRefs(_.pad['a'][1])}" >> PP
    f"  _.pad[\'b\'] -> {numRefs(_.pad['b'])}" >> PP
    f"  _.fred -> {numRefs(_.fred)}" >> PP

    "\n_.fred = 'fred'" >> PP
    _.fred = 'fred'
    f"_.pad => {_.pad}" >> PP
    f"_.fred => {_.fred}" >> PP
    f"  _.pad -> {numRefs(_.pad)}" >> PP
    f"  _.pad[\'a\'] -> {numRefs(_.pad['a'])}" >> PP
    f"  _.pad[\'a\'][1] -> {numRefs(_.pad['a'][1])}" >> PP
    f"  _.pad[\'b\'] -> {numRefs(_.pad['b'])}" >> PP
    f"  _.fred -> {numRefs(_.fred)}" >> PP

    "\n_.fred = _.pad['a']" >> PP
    # fred = _.pad['a']
    _.fred = _.pad['a']
    f"_.pad => {_.pad}" >> PP
    f"_.fred => {_.fred}" >> PP
    f"  _.pad -> {numRefs(_.pad)}" >> PP
    f"  _.pad[\'a\'] -> {numRefs(_.pad['a'])}" >> PP
    f"  _.pad[\'a\'][1] -> {numRefs(_.pad['a'][1])}" >> PP
    f"  _.pad[\'b\'] -> {numRefs(_.pad['b'])}" >> PP
    f"  _.fred -> {numRefs(_.fred)}" >> PP


    "\n_.pad['a'][2] = 'a2'" >> PP
    _.pad['a'][2] = 'a2'
    f"_.pad => {_.pad}" >> PP
    f"_.fred => {_.fred}" >> PP
    f"  _.pad -> {numRefs(_.pad)}" >> PP
    f"  _.pad[\'a\'] -> {numRefs(_.pad['a'])}" >> PP
    f"  _.pad[\'a\'][1] -> {numRefs(_.pad['a'][1])}" >> PP
    f"  _.pad[\'b\'] -> {numRefs(_.pad['b'])}" >> PP
    f"  _.fred -> {numRefs(_.fred)}" >> PP


    "\ndiamond" >> PP
    x = {'child':1}
    _.diamond = dict(a=dict(x=x), b=dict(x=x))
    x = None
    _.diamond >> PP
    f"  _.diamond -> {numRefs(_.diamond)}" >> PP
    f"  _.diamond['a'] -> {numRefs(_.diamond['a'])}" >> PP
    f"  _.diamond['a']['x'] -> {numRefs(_.diamond['a']['x'])}" >> PP
    f"  _.diamond['b'] -> {numRefs(_.diamond['b'])}" >> PP
    f"  _.diamond['b']['x'] -> {numRefs(_.diamond['b']['x'])}" >> PP

    with assertRaises(ProgrammerError):
        # fix this
        "\n_.diamond['a']['x'].update(dict(child=2))" >> PP
        _.diamond['a']['x'].update(dict(child=2))
        _.diamond >> PP
        f"  _.diamond -> {numRefs(_.diamond)}" >> PP
        f"  _.diamond['a'] -> {numRefs(_.diamond['a'])}" >> PP
        f"  _.diamond['a']['x'] -> {numRefs(_.diamond['a']['x'])}" >> PP
        f"  _.diamond['b'] -> {numRefs(_.diamond['b'])}" >> PP
        f"  _.diamond['b']['x'] -> {numRefs(_.diamond['b']['x'])}" >> PP


    "" >> PP

    len(_.pad) >> check >> equal >> 2
    _.pad.items() >> PP
    dir(_.pad) >> PP
    type(_.pad) >> PP

    with assertRaises(ProgrammerError):
        # fix this
        with context(halt=True):
            _.pad.update({'c':3})
        _.pad >> PP




def test_diamond_gets_broken():
    _ = _Scope()

    "\ndiamond" >> PP
    x = {'child':1}
    _.diamond = dict(a=dict(x=x), b=dict(x=x))
    x = None
    _.diamond >> PP
    f"  _.diamond -> {numRefs(_.diamond)}" >> PP
    f"  _.diamond['a'] -> {numRefs(_.diamond['a'])}" >> PP
    f"  _.diamond['a']['x'] -> {numRefs(_.diamond['a']['x'])}" >> PP
    f"  _.diamond['b'] -> {numRefs(_.diamond['b'])}" >> PP
    f"  _.diamond['b']['x'] -> {numRefs(_.diamond['b']['x'])}" >> PP

    "\n_.diamond['a']['x']['b2'] = _.diamond['b']" >> PP
    _.diamond['a']['x']['b2'] = _.diamond['b']
    _.diamond >> PP
    f"  _.diamond -> {numRefs(_.diamond)}" >> PP
    f"  _.diamond['a'] -> {numRefs(_.diamond['a'])}" >> PP
    f"  _.diamond['a']['x'] -> {numRefs(_.diamond['a']['x'])}" >> PP
    f"  _.diamond['b'] -> {numRefs(_.diamond['b'])}" >> PP
    f"  _.diamond['b']['x'] -> {numRefs(_.diamond['b']['x'])}" >> PP
    _.diamond['a'] >> PP
    _.diamond['b'] >> PP


    "\ndiamond" >> PP
    x = {'child':1}
    _.diamond = dict(a=dict(x=x), b=dict(x=x))
    x = None
    _.diamond >> PP
    f"  _.diamond -> {numRefs(_.diamond)}" >> PP
    f"  _.diamond['a'] -> {numRefs(_.diamond['a'])}" >> PP
    f"  _.diamond['a']['x'] -> {numRefs(_.diamond['a']['x'])}" >> PP
    f"  _.diamond['b'] -> {numRefs(_.diamond['b'])}" >> PP
    f"  _.diamond['b']['x'] -> {numRefs(_.diamond['b']['x'])}" >> PP

    "\n_.diamond['a']['x']['child'] = 2" >> PP
    _.diamond['a']['x']['child'] = 2
    _.diamond >> PP
    f"  _.diamond -> {numRefs(_.diamond)}" >> PP
    f"  _.diamond['a'] -> {numRefs(_.diamond['a'])}" >> PP
    f"  _.diamond['a']['x'] -> {numRefs(_.diamond['a']['x'])}" >> PP
    f"  _.diamond['b'] -> {numRefs(_.diamond['b'])}" >> PP
    f"  _.diamond['b']['x'] -> {numRefs(_.diamond['b']['x'])}" >> PP


def test_detect_parent_cycle():
    _ = _Scope()
    _.pad = {'a': {1:'a1'}}
    with assertRaises(ValueError):
        _.pad['a'][3] = _.pad


def test_append():
    _ = _Scope()

    _.a = tvstruct()
    _.a = []
    _.b = _.a
    _.a.append(1)
    assert len(_.a) == 1
    assert len(_.b) == 0

    _.pad = tvstruct()
    _.pad.a = []
    _.c = _.pad.a
    _.pad.a.append(1)
    assert len(_.pad.a) == 1
    assert len(_.c) == 0



def main():
    test_iters()
    test_scope()
    test_cow()
    test_detect_parent_cycle()
    test_diamond_gets_broken()
    test_append()


if __name__ == '__main__':
    main()
    print('pass')

