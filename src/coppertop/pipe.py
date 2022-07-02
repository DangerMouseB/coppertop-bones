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

import sys
if hasattr(sys, '_TRACE_IMPORTS') and sys._TRACE_IMPORTS: print(__name__)

__all__ = [
    'coppertop', 'nullary', 'unary', 'rau', 'binary', 'ternary', 'unary1', 'binary2', '_', 'sig', 'context',
    'raiseLessPipe', 'typeOf', 'selectDispatcher', 'anon', 'MultiFn', 'Partial'
]


import inspect, types, datetime, builtins
from collections import namedtuple
from coppertop.core import context
from coppertop._singletons import _CoWProxy, _TBC_AND_CONTEXT, CoppertopError
from bones.core.errors import ProgrammerError, NotYetImplemented, PathNotTested, ErrSite
from bones.core.sentinels import Missing
from bones.core.utils import firstKey
from bones.lang.metatypes import BType, fitsWithin, cacheAndUpdate, BTFn, BTUnion, BTTuple, BTPrimitive
from bones.lang.types import nullary, unary, binary, ternary, rau, void
from coppertop.types import py

unary1 = BTPrimitive.ensure("unary1")
binary2 = BTPrimitive.ensure("binary2")

_BonesTByPythonT = {}

def _initBonesTByPythonT():
    # easiest way to keep namespace relatively clean
    from ribs.types import txt, date, bool, litint, litdec
    from coppertop.types import pytuple, pylist

    _BonesTByPythonT.update({
        builtins.int: litint,
        builtins.str: txt,
        datetime.date: date,
        builtins.float: litdec,
        builtins.bool: bool,
        builtins.tuple: pytuple,
        builtins.list: pylist,
    })

_initBonesTByPythonT()



DispatcherQuery = namedtuple('DispatcherQuery', ['d', 'tByT'])

_ = _TBC_AND_CONTEXT
NOT_OPTIONAL = inspect._empty    # this is the sentinel python uses to indicate that an argument has no default (i.e. is optional)
NO_ANNOTATION = inspect._empty    # this is the sentinel python uses to indicate that an argument has no annotation
BETTER_ERRORS = False
DEFAULT_BMODULE_NAME = 'main'

_mfByFnnameByBmodname = {}
_sigCache = {}




# the @coppertop decorator
def coppertop(*args, style=Missing, newName=Missing, typeHelper=Missing, supressDispatcherQuery=False, patch=Missing):

    def registerFn(fn):
        patching = patch is not Missing
        style_ = unary if style is Missing else style
        bmodule, pymodule, fnname, priorDef, definedInFunction, argNames, sig, tRet, pass_tByT = _fnContext(fn, 'registerFn', newName)
        if patching:
            bmodule = patch
        elif bmodule is Missing:
            if priorDef:
                # if we have imported a function and are extending it then use its bmodule
                if isinstance(priorDef.dispatcher, _MultiDispatcher):
                    for dBySig in priorDef.dispatcher.dBySigByNumArgs:
                        if dBySig:
                            bmodule = firstKey(dBySig.values()).bmodule
                            break
                else:
                    bmodule = priorDef.dispatcher.bmodule
            else:
                bmodule = DEFAULT_BMODULE_NAME

        # create dispatcher
        partialCls = _PartialClassByStyle[style_]
        bonesStyle = unary if style_ == unary1 else (binary if style_ == binary2 else style_)
        if issubclass(partialCls, Partial):
            d = _SingleDispatcher(partialCls, fnname, bmodule, pymodule, bonesStyle, fn, supressDispatcherQuery, typeHelper, BTFn(BTTuple(*sig), tRet), argNames, pass_tByT)
        elif issubclass(partialCls, _FasterSingleDispatcher):
            d = partialCls(Missing, fnname, bmodule, pymodule, bonesStyle, fn, supressDispatcherQuery, typeHelper, BTFn(BTTuple(*sig), tRet), argNames, pass_tByT)
        else:
            raise ProgrammerError()

        # add it to the relevant multifn
        if definedInFunction:
            # create a new multifunction for use in this function
            # do not inherit any multifn not defined or imported into this module
            if patching: raiseLessPipe(CoppertopError('Patch is not allowed within a function', ErrSite("#1")))
            if priorDef:
                d = _MultiDispatcher(priorDef.dispatcher, d)
            mf = MultiFn(fnname)
        else:
            if patching:
                # ignore priorDef
                mfByFnname = _mfByFnnameByBmodname.setdefault(bmodule, {})
                mf = mfByFnname.get(fnname, Missing)
                if mf is Missing:
                    mf = MultiFn(fnname)
                    mfByFnname[fnname] = mf
                else:
                    d = _extendDispatcher(mf.dispatcher, d, patching)
            elif priorDef and isinstance(priorDef, _DispatcherBase):
                mf = priorDef
                d = _extendDispatcher(mf.dispatcher, d, patching)
            else:
                mfByFnname = _mfByFnnameByBmodname.setdefault(bmodule, {})
                mf = mfByFnname.get(fnname, Missing)
                if mf is Missing:
                    mf = MultiFn(fnname)
                    mfByFnname[fnname] = mf
                else:
                    d = _extendDispatcher(mf.dispatcher, d, patching)
        mf.dispatcher = d
        return mf

    if len(args) == 1 and isinstance(args[0], (types.FunctionType, types.MethodType, type)):
        # of form @coppertop so args[0] is the function or class being decorated
        return registerFn(args[0])

    else:
        # of form as @coppertop() or @coppertop(overrideLHS=True) etc
        if len(args): raiseLessPipe(TypeError('Only kwargs allowed', ErrSite("#2")))
        return registerFn


# NOTE
# the ability to extend changes the way the programmer thinks of types - and it makes tags much more desireable
# to the programmer which in turn makes inference easier.
#
# e.g. consider fn fred(x). With no type information it cannot be extended by the programmer as they cannot
# indicate the situation in which the original should be called and in which the extension should be called. Thus
# they tend to say a particular function is only callable by a restricted set of types, e.g. integers. joe(x:int)
# can be easily extended with joe(x:txt).
#
# (actually in cpt-b fred(x) can be extended with fred(x:int) as we match functions using a distance metric where
# no type is further away than exact type so the exact type matches - but fred(x) cannot be extended with fred(x) )

def _extendDispatcher(currentDispatcher, newDispatcher, patching):
    # OPEN: if we are extending something in another module we might want an error thrown if we are redefining a
    #       function (i.e. with the same signature)

    # if newDispatcher.bmodule != currentDispatcher.bmodule:
    #     raiseLessPipe(CoppertopError(
    #         f'Trying to extend {currentDispatcher.bmodule}.{currentDispatcher.fnname} with {newDispatcher.bmodule}.{newDispatcher.fnname} - module conflict - use patch'))

    # extend the current multifn with d
    sig = "sig"
    if False:  # sig is already defined
        if patching or newDispatcher.pymodule == currentDispatcher.pymodule:
            # remove sig from dispatchers
            pass
        else:
            raiseLessPipe(CoppertopError( f'Trying to redefine {currentDispatcher.bmodule}.{currentDispatcher.fnname} with {newDispatcher.bmodule}.{newDispatcher.fnname} - module conflict - use patch', ErrSite("#1")))

    return _MultiDispatcher(currentDispatcher, newDispatcher)



class MultiFn(object):
    __slots__ = ['_dispatcher', 'name']

    def __init__(self, name):
        self._dispatcher = Missing
        self.name = name
    def __call__(self, *args, **kwargs):
        return self.dispatcher.__call__(*args, **kwargs)
    def __rrshift__(self, arg):  # arg >> func
        if isinstance(arg, MultiFn): arg = arg.dispatcher
        answer = arg >> self.dispatcher
        return answer
    def __rshift__(self, arg):  # func >> arg
        if isinstance(arg, MultiFn): arg = arg.dispatcher
        return self.dispatcher >> arg
    def __repr__(self):
        return self.dispatcher.__repr__()
    @property
    def dispatcher(self):
        return self._dispatcher
    @dispatcher.setter
    def dispatcher(self, d):
        self._dispatcher = d
    @property
    def __doc__(self):
        return self._dispatcher.__doc__
    @property
    def _t(self):
        return self.dispatcher._t


class _DispatcherBase(object):

    def __call__(d, *args, **kwargs):  # func(...)
        # if all the args are passed and not a multi dispatcher then we don't need to create a partial
        # would this be overall faster? yes as this is calculated anyway in Partial.__new__
        return d.partialCls(d, False, args, kwargs)

    def __rrshift__(d, arg):  # arg >> func
        if d.partialCls.numLeft == 0:
            raiseLessPipe(CoppertopError(f'arg >> {d.name} - illegal syntax for a {d.style}', ErrSite(d.__class__, "illegal syntax")))
        else:
            args = [_TBC_AND_CONTEXT] * d.partialCls.numPiped
            return d.partialCls(d, False, args, {}).__rrshift__(arg)

    def __rshift__(d, arg):  # func >> arg
        if d.partialCls.numLeft == 0 and d.partialCls.numRight > 0:
            # only rau_ can handle this case
            args = [_TBC_AND_CONTEXT] * d.partialCls.numRight
            return d.partialCls(d, False, args, {}).__rshift__(arg)
        else:
            if hasattr(arg, '__rrshift__'):
                return arg.__rrshift__(d)
            else:
                raiseLessPipe( CoppertopError(f'{d.name} >> arg - illegal syntax for a {d.style}', ErrSite(d.__class__, "illegal syntax")))

    def __repr__(d):
        return d.name

    def _dispatch(d, args, kwargs):
        io = dict(hasValue=False)
        sig = builtins.tuple(((arg if _isType(arg, io) else _typeOf(arg)) for arg in args))
        sd, tByT = d._selectDispatcher(sig)
        if io['hasValue'] or sd.supressDispatcherQuery:
            return _dispatchNoSigCheck(sd, args, kwargs, tByT)
        else:
            return DispatcherQuery(sd, tByT)



class _SingleDispatcher(_DispatcherBase):

    def __init__(sd, partialCls, name, bmodule, pymodule, style, fn, supressDispatcherQuery, typeHelper, _t, argNames, pass_tByT):
        sd.partialCls = partialCls
        sd.name = name
        sd.bmodule = bmodule
        sd.pymodule = pymodule
        sd.style = style
        sd.fn = fn
        sd._argNames = argNames
        sd._sig = _t.tArgs.types
        sd._tArgs = _t.tArgs
        sd._tRet = _t.tRet
        sd._t_ = Missing
        sd._numArgsNeeded = len(sd._sig)
        sd.pass_tByT = pass_tByT
        sd.supressDispatcherQuery = supressDispatcherQuery          # calls the function rather than returns the dispatch when all args are types
        sd.typeHelper = typeHelper
        sd.tByT_ByTArgs = {}
        sd.__doc__ = fn.__doc__ if hasattr(fn, '__doc__') else None

    def _selectDispatcher(sd, callerSig):
        return _checkDispatcherForSD(callerSig, sd)

    @property
    def fullname(sd):
        return sd.bmodule + '.' + sd.name

    @property
    def sig(sd):
        return sd._sig

    @property
    def numargs(sd):
        return len(sd._sig)

    @property
    def tArgs(sd):
        return sd._tArgs

    @property
    def tRet(sd):
        return sd._tRet

    @property
    def _t(sd):
        if sd._t_ is Missing:
            sd._t_ = BTFn(BTTuple(*sd._tArgs), sd._tRet)
        return sd._t_



class _MultiDispatcher(_DispatcherBase):

    def __new__(cls, *dispatchers):
        name = dispatchers[0].name
        style = dispatchers[0].style
        ds = []
        maxNumArgs = 0
        for d in dispatchers:
            if isinstance(d, _MultiDispatcher):
                if len(d.dBySigByNumArgs) > maxNumArgs: maxNumArgs = len(d.dBySigByNumArgs)
            elif isinstance(d, _FasterSingleDispatcher):
                if len(d.sig) > maxNumArgs: maxNumArgs = len(d.sig)
            elif isinstance(d, _SingleDispatcher):
                if len(d.sig) > maxNumArgs: maxNumArgs = len(d.sig)
        dBySigByNumArgs = [{} for i in range(maxNumArgs + 1)]
        for d in dispatchers:
            if isinstance(d, _MultiDispatcher):
                for dBySig in d.dBySigByNumArgs:
                    for d in dBySig.values():
                        if isinstance(d, _FasterSingleDispatcher):
                            if style == unary:
                                if d.style != unary: raise TypeError(f'{name}() is unary - can\'t change to {d.style}',ErrSite(cls, "#1"))
                            elif style == binary:
                                if d.style != binary: raise TypeError(f'{name}() is binary - can\'t change it to {d.style}', ErrSite(cls, "#2"))
                            else:
                                raiseLessPipe(ProgrammerError('unhandled _FasterSingleDispatcher subclass', ErrSite(cls, "#3")))
                            ds.append(d)
                        elif isinstance(d, _SingleDispatcher):
                            if d.style != style:
                                raiseLessPipe(TypeError(f'Expected {style} got {d.style}', ErrSite(cls, "#4")))
                            ds.append(d)
                        else:
                            raiseLessPipe(ValueError("unknown dispatcher type", ErrSite(cls, "#5")))
            elif isinstance(d, _FasterSingleDispatcher):
                if style == unary:
                    if d.style != unary: raise TypeError(f'{name}() is unary - can\'t change to {d.style}', ErrSite(cls, "#6"))
                elif style == binary:
                    if d.style != binary: raise TypeError(f'{name}() is binary - can\'t change it to {d.style}', ErrSite(cls, "#7"))
                else:
                    raiseLessPipe(ProgrammerError(f'{d.pymodule}.{d.name} - unhandled _FasterSingleDispatcher subclass', ErrSite(cls, "#8")))
                ds.append(d)
            elif isinstance(d, _SingleDispatcher):
                if d.name != name: raise ProgrammerError(ErrSite(cls, "#9"))
                if d.style != style: raiseLessPipe(TypeError(f'When processing @coppertop for function {name} - expected style={style} got {d.style}', ErrSite(cls, "#10")))
                ds.append(d)
            else:
                raiseLessPipe(ProgrammerError("unhandled dispatcher class", ErrSite(cls, "#11")))
        for d in ds:
            oldD = dBySigByNumArgs[len(d.sig)].get(d.sig, Missing)
            if oldD is not Missing and oldD.pymodule != d.pymodule:
                raise CoppertopError(f'Found definition of {_ppFn(name, d.sig)} in "{d.pymodule}" and "{oldD.pymodule}"', ErrSite(cls, "#12"))
            dBySigByNumArgs[len(d.sig)][d.sig] = d
        if len(dBySigByNumArgs) == 1 and len(dBySigByNumArgs[0]) == 1:
            # this can occur in a REPL where a function is being redefined
            # SHOULDDO think this through as potentially we could overload functions in the repl accidentally which
            #  would be profoundly confusing
            return d
        md = super().__new__(cls)
        md.partialCls = _PartialClassByStyle[style]
        md.name = name
        md.style = style
        md.dBySigByNumArgs = dBySigByNumArgs
        md.dtByT_ByTArgsByNumArgs = [{} for i in range(maxNumArgs + 1)]
        md._t_ = Missing
        md._checkMDDef()
        md.__doc__ = None
        return md

    @property
    def _t(md):
        if md._t_ is Missing:
            ts = []
            for dBySig in md.dBySigByNumArgs:
                for d in dBySig.values():
                    ts.append(d._t)
            md._t_ = BTUnion(*ts)
        return md._t_

    def _selectDispatcher(md, callerSig):
        return _selectDispatcherFromMD(callerSig, md)

    def _checkMDDef(md):
        overlap = False
        if overlap: raiseLessPipe(CoppertopError("The signatures of the provided dispatcher do not uniquely resolve"), ErrSite(md.__class__, "#1"))


class _FasterSingleDispatcher(_SingleDispatcher):
    # removes a couple of calls compared to _SingleDispatch (faster and easier to step through)
    def __init__(fsd, partialCls, name, bmodule, pymodule, style, fn, supressDispatcherQuery, typeHelper, _t, argNames, pass_tByT):
        super().__init__(partialCls, name, bmodule, pymodule, style, fn, supressDispatcherQuery, typeHelper, _t, argNames, pass_tByT)
    def __call__(fsd, *args, **kwargs):  # func(...)
        raiseLessPipe(CoppertopError(f'Illegal syntax {fsd.name}(...)', ErrSite(fsd.__class__, "#1")))
    def __rrshift__(fsd, arg):  # arg >> func
        raiseLessPipe(CoppertopError(f'Illegal syntax arg >> {fsd.name}', ErrSite(fsd.__class__, "#1")))
    def __rshift__(fsd, arg):    # func >> arg
        if hasattr(arg, '__rrshift__'):
            try:
                return arg.__rrshift__(fsd)
            except:
                return NotImplemented
        else:
            raiseLessPipe(CoppertopError(f'{fsd.name} >> arg - illegal syntax for a {fsd.style.name}', ErrSite(fsd.__class__, "#1")))


class unary1_(_FasterSingleDispatcher):
    name = 'unary1'
    numPiped = 1
    numLeft = 1
    numRight = 0
    def __call__(u1, *args, **kwargs):  # func(arg)
        arg = args[0]
        io = dict(hasValue=False)
        sigCaller = (arg if _isType(arg, io) else _typeOf(arg),)
        d, tByT = _checkDispatcherForU1(sigCaller, u1)
        if io['hasValue'] or d.supressDispatcherQuery:
            return _dispatchNoSigCheck(d, args, kwargs, tByT)
        else:
            return DispatcherQuery(d, tByT)
    def __rrshift__(u1, arg):  # arg >> func
        io = dict(hasValue=False)
        sigCaller = (arg if _isType(arg, io) else _typeOf(arg),)
        d, tByT = _checkDispatcherForU1(sigCaller, u1)
        if io['hasValue'] or d.supressDispatcherQuery:
            return _dispatchNoSigCheck(d, (arg,), {}, tByT)
        else:
            return DispatcherQuery(d, tByT)


class binary2_(_FasterSingleDispatcher):
    name = 'binary2'
    numPiped = 2
    numLeft = 1
    numRight = 1
    def __call__(b2, *args, **kwargs):  # func(arg1, arg2)
        arg1, arg2 = args
        if arg1 is _TBC_AND_CONTEXT or arg2 is _TBC_AND_CONTEXT: return _PartialBinary2(b2, arg1, arg2)
        io = dict(hasValue=False)
        sigCaller = (arg1 if _isType(arg1, io) else _typeOf(arg1), arg2 if _isType(arg2, io) else _typeOf(arg2))
        d, tByT = _checkDispatcherForB2(sigCaller, b2)
        if io['hasValue'] or d.supressDispatcherQuery:
            return _dispatchNoSigCheck(d, args, kwargs, tByT)
        else:
            return DispatcherQuery(d, tByT)
    def __rrshift__(b2, arg1):  # arg1 >> func
        return _PartialBinary2(b2, arg1, _TBC_AND_CONTEXT)
class _PartialBinary2(object):
    def __init__(pb2, b2, arg1, arg2):
        pb2.b2 = b2
        pb2.arg1 = arg1
        pb2.arg2 = arg2
    def __rshift__(pb2, arg2):  # func >> arg2
        return pb2._dispatch(arg2)
    def __call__(pb2, arg):  # func >> arg2
        return pb2._dispatch(arg)
    def _dispatch(pb2, arg):
        if pb2.arg1 is _TBC_AND_CONTEXT: arg1 = arg; arg2 = pb2.arg2
        if pb2.arg2 is _TBC_AND_CONTEXT: arg1 = pb2.arg1; arg2 = arg
        io = dict(hasValue=False)
        callerSig = (arg1 if _isType(arg1, io) else _typeOf(arg1), arg2 if _isType(arg2, io) else _typeOf(arg2))
        d, tByT = checkDispatcherForPB2(callerSig, pb2)
        if io['hasValue'] or d.supressDispatcherQuery:
            return _dispatchNoSigCheck(d, (arg1, arg2), {}, tByT)
        else:
            return DispatcherQuery(d, tByT)


class Partial(object):
    name = 'Partial'
    numPiped = 0
    numLeft = 0
    numRight = 0

    def __new__(cls, dispatcher, isPiping, args, kwargs):
        numArgsGiven = len(args)
        if numArgsGiven < cls.numPiped:
            raiseLessPipe(CoppertopError(f'{dispatcher.name} needs at least {cls.numPiped} arg' + ('s' if (cls.numPiped > 1) else ''), ErrSite(cls, "#1")))
        if not (iTBC := [i for (i, a) in enumerate(args) if a is _TBC_AND_CONTEXT]):     # if a is an numpy.ndarray then == makes things weird
            return dispatcher._dispatch(args, kwargs)
        else:
            p = super().__new__(cls)
            p.dispatcher = dispatcher
            p.args = args
            p.kwargs = kwargs
            p.numArgsGiven = numArgsGiven
            p.iTBC = iTBC
            p.isPiping = isPiping   # True if a >> has been encountered
            p._t_ = Missing
            p.tByT_ByTArgs = {}
            return p

    def __call__(p, *args, **kwargs):
        if p.isPiping: raiseLessPipe(CoppertopError(f'syntax not of form {_prettyForm(p)}', ErrSite(p.__class__, "#1")))
        if len(args) > len(p.iTBC): raiseLessPipe(CoppertopError(f'{p.dispatcher.name} - too many args - got {len(args)} needed {len(p.iTBC)}', ErrSite(p.__class__, "#2")))
        newArgs =  _atPut(p.args, p.iTBC[0:len(args)], args)
        newKwargs = dict(p.kwargs)
        newKwargs.update(kwargs)
        return p.__class__(p.dispatcher, False, newArgs, newKwargs)

    def __rrshift__(p, arg):  # arg >> func
        if p.numLeft == 0:
            # if we are here then the arg does not implement __rshift__ so this is a syntax error
            raiseLessPipe(CoppertopError(f'syntax not of form {_prettyForm(p)}', ErrSite(p.__class__, "numLeft == 0")))
        else:
            if p.isPiping: raiseLessPipe(CoppertopError(f'For {p.dispatcher.name} - syntax is not of form {_prettyForm(p)}', ErrSite(p.__class__, "isPiping")))
            if len(p.iTBC) != p.numPiped:
                raiseLessPipe(CoppertopError(f'{p.dispatcher.name} needs {len(p.iTBC)} args but {p.numPiped} will be piped', ErrSite(p.__class__, "#3")))
            newArgs = _atPut(p.args, p.iTBC, [arg] + [_TBC_AND_CONTEXT] * (p.numPiped - 1))
            return p.__class__(p.dispatcher, True, newArgs, p.kwargs)

    def __rshift__(p, arg):  # func >> arg
        if p.numRight == 0:
            return NotImplemented
        else:
            if isinstance(p, rau_):
                if isinstance(arg, _SingleDispatcher):
                    if arg.style in (nullary, unary, binary, ternary):
                        raiseLessPipe(TypeError(f'An rau_ may not consume a nullary, unary, binary, ternary', ErrSite(p.__class__, "#1")))
                    if arg.style == rau:
                        raiseLessPipe(NotYetImplemented('could make sense...', ErrSite(p.__class__, "#2")))
                if len(p.iTBC) != p.numPiped: raise CoppertopError(f'needs {len(p.iTBC)} args but {p.numPiped} will be piped', ErrSite(p.__class__, "#3"))
                newArgs = _atPut(p.args, p.iTBC[0:1], [arg])
            elif isinstance(p, binary_):
                if not p.isPiping: raiseLessPipe(CoppertopError(f'syntax not of form {_prettyForm(p)}', ErrSite(p.__class__, "#4")))
                if isinstance(arg, MultiFn) and arg.dispatcher.style is rau:
                    raiseLessPipe(NotYetImplemented(
                        f'>> binary_ >> rau_ >> x not yet implemented use parentheses >> binary_ >> (rau_ >> x)',
                        ErrSite(p.__class__, '>> binary_ >> rau_ >> x nyi')
                    ))
                newArgs = _atPut(p.args, p.iTBC[0:1], [arg])
            elif isinstance(p, ternary_):
                if not p.isPiping: raiseLessPipe(CoppertopError(f'syntax not of form {_prettyForm(p)}', ErrSite(p.__class__, "#5")))
                if len(p.iTBC) == 2:
                    if isinstance(arg, MultiFn) and arg.dispatcher.style is rau:
                        raiseLessPipe(NotYetImplemented(
                            f'>> ternary_ >> rau_ >> x >> y not yet implemented use parentheses >> ternary_ >> (rau_ >> x) >> y',
                            ErrSite(p.__class__, '>> ternary_ >> rau_ >> x >> y nyi')
                        ))
                    newArgs = _atPut(p.args, p.iTBC[0:2], [arg, _TBC_AND_CONTEXT])
                elif len(p.iTBC) == 1:
                    if isinstance(arg, MultiFn) and arg.dispatcher.style is rau:
                        raiseLessPipe(NotYetImplemented(
                            f'>> ternary_ >> x >> rau_ >> y not yet implemented use parentheses >> ternary_ >> x >> (rau_ >> y)',
                            ErrSite(p.__class__, '>> ternary_ >> x >> rau_ >> y nyi')
                        ))
                    newArgs = _atPut(p.args, p.iTBC[0:1], [arg])
                else:
                    raiseLessPipe(ProgrammerError(ErrSite(p.__class__, "#6")))
            else:
                raiseLessPipe(ProgrammerError(ErrSite(p.__class__, "#7")))
            return p.__class__(p.dispatcher, True, newArgs, p.kwargs)

    def __repr__(p):
        return f"{p.dispatcher.name}({', '.join([repr(arg) for arg in p.args])})"

    @property
    def sig(p):
        sig = p.dispatcher.sig
        return builtins.tuple(sig[i] for i in p.iTBC)

    @property
    def tRet(p):
        return p.dispatcher._tRet

    @property
    def _t(p):
        # OPEN: could check that the number of arguments in the partial doesn't exceed the number of args in the
        # multidispatcher - the available dispatchers for a partial could be filtered from the md on each partial creation?
        # lots of extra work - just filter once on dispatch? actually not a problem as length is handled in the
        # dispatcher selection.
        if p._t_ is Missing:
            try:
                if isinstance(p.dispatcher, _SingleDispatcher):
                    try:
                        sig = [p.dispatcher.sig[iTBC] for iTBC in p.iTBC]
                    except IndexError:
                        # number of args error so we know this dispatcher will not be found so throw a TypeError
                        raise TypeError('Needs more description', ErrSite(p.__class__, "#1"))
                    t = BTFn(BTTuple(*sig), p.dispatcher._tRet)
                elif isinstance(p.dispatcher, _MultiDispatcher):
                    ts = []
                    for dBySig in p.dispatcher.dBySigByNumArgs:
                        for sig, d in dBySig.items():
                            try:
                                sig = [sig[iTBC] for iTBC in p.iTBC]
                            except IndexError:
                                # number of args error so we know this dispatcher will not be found so ignore
                                raise ProgrammerError()
                            t = BTFn(BTTuple(*sig), d._tRet)
                            ts.append(t)
                    if len(ts) == 0:
                        raise TypeError('Needs more description', ErrSite(p.__class__, "#2"))
                    elif len(ts) == 1:
                        t = ts[0]
                    else:
                        t = BTUnion(*ts)
                else:
                    raise ProgrammerError("missing dispatcher type", ErrSite(p.__class__, "#3"))
            except TypeError as ex:
                raise
            except Exception as ex:
                print(p.dispatcher.sig if isinstance(p.dispatcher, _SingleDispatcher) else p.dispatcher.dBySig.values())
                print(p.iTBC)
                print(p.dispatcher._tRet)
                raise TypeError(f'Can\t generate type on partially bound {d.name} - needs more detail in this error message', ErrSite(p.__class__, "#4"))
            p._t_ = t
        return p._t_


class nullary_(Partial):
    name = 'nullary_'
    numPiped = 0
    numLeft = 0
    numRight = 0

class unary_(Partial):
    name = 'unary_'
    numPiped = 1
    numLeft = 1
    numRight = 0

class rau_(Partial):
    name = 'rau_'
    numPiped = 1
    numLeft = 0
    numRight = 1

class binary_(Partial):
    name = 'binary_'
    numPiped = 2
    numLeft = 1
    numRight = 1

class ternary_(Partial):
    name = 'ternary_'
    numPiped = 3
    numLeft = 1
    numRight = 2



def _checkDispatcherForU1(sigCaller, u1):
    doesFit, tByT = _fitsSignature(sigCaller, u1.sig)
    if not doesFit:
        # DOES_NOT_UNDERSTAND
        raiseLessPipe(TypeError(f"Can't find {u1.name}{str(sigCaller)}", ErrSite("does not understand")))
    return u1, tByT

def _checkDispatcherForB2(sigCaller, b2):
    doesFit, tByT = _fitsSignature(sigCaller, b2.sig)
    if not doesFit:
        # DOES_NOT_UNDERSTAND
        raiseLessPipe(TypeError(f"Can't find {b2.name}{str(sigCaller)}", ErrSite("does not understand")))
    return b2, tByT

def checkDispatcherForPB2(sigCaller, pb2):
    doesFit, tByT = _fitsSignature(sigCaller, pb2.b2.sig)
    if not doesFit:
        # DOES_NOT_UNDERSTAND
        raiseLessPipe(TypeError(f"Can't find {pb2.b2.name}{str(sigCaller)}", ErrSite("does not understand")))
    return pb2.b2, tByT

def _checkDispatcherForSD(sigCaller, sd):
    numArgs = len(sigCaller)
    tByT = sd.tByT_ByTArgs.get(sigCaller, Missing)
    if tByT is Missing:   
        match = False
        if numArgs == len(sd.sig):            # caller is likely passing optional arguments
            match = True
            argDistances = []
            tByT = {}
            for tArg, tSig in zip(sigCaller[0:len(sd.sig)], sd.sig):
                if tSig is py:
                    pass
                else:
                    doesFit, tByT, argDistance = cacheAndUpdate(fitsWithin(tArg, tSig), tByT, 0)
                    if not doesFit:
                        match = False
                        break
                    argDistances.append(argDistance)
            distance = sum(argDistances)
        if not match:
            # DOES_NOT_UNDERSTAND`
            with context(showFullType=True):
                lines = [
                    f"Can't find {_ppFn(sd.name, sigCaller)} in:",
                    f'  {_ppFn(sd.name, sd.sig, sd._argNames)} in {sd.bmodule} - {sd.pymodule}'
                ]
                print('\n'.join(lines), file=sys.stderr)
                raiseLessPipe(TypeError('\n'.join(lines), ErrSite("#1")))
        sd.tByT_ByTArgs[sigCaller] = tByT
    return sd, tByT

def _selectDispatcherFromMD(sigCaller, md):
    numArgs = len(sigCaller)
    d, tByT = md.dtByT_ByTArgsByNumArgs[numArgs].get(sigCaller, (Missing, {}))
    if d is Missing:
        matches = []
        fallbacks = []
        # search though each bound function ignoring discrepancies where the declared type is py
        for dSig, d in md.dBySigByNumArgs[numArgs].items():
            distance = 10000
            fallback = False
            match = True
            argDistances = []
            tByT = {}
            for tArg, tSig in zip(sigCaller, dSig):
                if tSig is py:
                    fallback = True
                    argDistances.append(0.5)
                else:
                    doesFit, tByT, argDistance = cacheAndUpdate(fitsWithin(tArg, tSig, False), tByT, 0)
                    if not doesFit:
                        match = False
                        break
                    argDistances.append(argDistance)
            if match:
                distance = sum(argDistances)
                if fallback:
                    fallbacks.append((d, tByT, distance, argDistances))
                else:
                    matches.append((d, tByT, distance, argDistances))
            if distance == 0:
                break
        if distance == 0:
            d, tByT, distance, argDistances = matches[-1]
        elif len(matches) == 0 and len(fallbacks) == 0:
            raiseLessPipe(_cantFindMatchError(md, sigCaller), ErrSite("#1"))
        elif len(matches) == 1:
            d, tByT, distance, argDistances = matches[0]
        elif len(matches) == 0 and len(fallbacks) == 1:
            d, tByT, distance, argDistances = fallbacks[0]
        elif len(matches) > 0:
            matches.sort(key=lambda x: x[2])
            # MUSTDO warn of potential conflicts that have not been explicitly noted
            if matches[0][2] != matches[1][2]:
                d, tByT, distance, argDistances = matches[0]
            else:
                # DOES_NOT_UNDERSTAND
                # too many at same distance so report the situation nicely
                caller = f'{md.name}({",".join([repr(e) for e in sigCaller])})'
                print(f'{caller} fitsWithin:', file=sys.stderr)
                for d, tByT, distance, argDistances in matches:
                    callee = f'{d.name}({",".join([repr(argT) for argT in d.sig])}) (argDistances: {argDistances}) defined in {d.bmodule}<{d.pymodule}>'
                    print(f'  {callee}', file=sys.stderr)
                raiseLessPipe(TypeError(f'Found {len(matches)} matches and {len(fallbacks)} fallbacks for {caller}', ErrSite("#2")))
        elif len(fallbacks) > 0:
            fallbacks.sort(key=lambda x: x[2])
            # MUSTDO warn of potential conflicts that have not been explicitly noted
            if fallbacks[0][2] != fallbacks[1][2]:
                d, tByT, distance, argDistances = fallbacks[0]
            else:
                # DOES_NOT_UNDERSTAND
                # too many at same distance so report the situation nicely
                caller = f'{md.name}({",".join([repr(e) for e in sigCaller])})'
                print(f'{caller} fitsWithin:', file=sys.stderr)
                for d, tByT, distance, argDistances in matches:
                    callee = f'{d.name}({",".join([repr(argT) for argT in d.sig])}) (argDistances: {argDistances}) defined in {d.pymodule}'
                    print(f'  {callee}', file=sys.stderr)
                raiseLessPipe(TypeError(f'Found {len(matches)} matches and {len(fallbacks)} fallbacks for {caller}', ErrSite("#3")))
        else:
            raise ProgrammerError('Can\'t get here', ErrSite("#4"))
        md.dtByT_ByTArgsByNumArgs[numArgs][sigCaller] = d, tByT
    return d, tByT

def _fitsSignature(sigCaller, sig):
    if len(sigCaller) != len(sig): return False
    match, tByT = _sigCache.get((sigCaller, sig), (Missing, {}))
    if match is Missing:
        distances = Missing
        match = True
        for i, tArg in enumerate(sigCaller):
            tSig = sig[i]
            if tSig == py:
                pass
            else:
                doesFit, tByT, distances = cacheAndUpdate(fitsWithin(tArg, tSig), tByT, distances)
                if not doesFit:
                    match = False
                    break
        _sigCache[(sigCaller, sig)] = match, tByT
    return match, tByT


def _dispatchNoSigCheck(d, args, kwargs, tByT):
    _tRet = d._tRet
    if d.pass_tByT:
        if d.typeHelper:
            tByT = d.typeHelper(*args, tByT=tByT, **kwargs)
        answer = d.fn(*args, tByT=tByT, **kwargs)
    else:
        if BETTER_ERRORS:
            answer = _callWithBetterErrors(d, args, kwargs)
        else:
            answer = d.fn(*args, **kwargs)
    if _tRet == py or isinstance(answer, DispatcherQuery):
        return answer
    else:
        # MUSTDO
        # BTTuples are products whereas pytuples are exponentials therefore we can reliably type check an answered
        # sequence if the return type is BTTuple (and possibly BTStruct) - also BTTuple can be coerced by default to
        # a tvseq (or similar - may should add a new tuple subclass to prevent it being treated like an exponential)
        # add a note in bones that one of our basic ideas / building blocks is things and exponentials of things

        doesFit, tByT, distances = cacheAndUpdate(fitsWithin(_typeOf(answer), _tRet), tByT)
        if doesFit:
            return answer
        else:
            raiseLessPipe(TypeError(f'{d.fullname} returned a {str(_typeOf(answer))} should have have returned a {d._tRet} {tByT}', ErrSite("#1")))


# better error messages
# instead of the Python one:
#       TypeError: createBag() missing 1 required positional argument: 'otherHandSizesById'
#
# TypeError: createBag() does match createBag(handId:any, hand:any, otherHandSizesById:any) -> cluedo_bag
# even better say we can't find a match for two arguments

def _callWithBetterErrors(d, args, kwargs):
    try:
        return d.fn(*args, **kwargs)
    except TypeError as ex:
        if ex.args and ' required positional argument'in ex.args[0]:
            print(_sig(d), file=sys.stderr)
            print(ex.args[0], file=sys.stderr)
        raiseLessPipe(ex, True)
        # argTs = [_ppType(argT) for argT in args]
        # retT = _ppType(x._tRet)
        # return f'({",".join(argTs)})->{retT} <{x.style.name}>  :   in {x.fullname}'


def _cantFindMatchError(md, sig):
    with context(showFullType=True):
        # DOES_NOT_UNDERSTAND
        print(f"Can't find {_ppFn(md.name, sig)} in:", file=sys.stderr)
        for dBySig in md.dBySigByNumArgs:
            for dSig, d in dBySig.items():
                print(f'  {_ppFn(d.name, dSig)} in {d.bmodule} - {d.fullname}', file=sys.stderr)
        return TypeError(f"Can't find {_ppFn(md.name, sig)}")


def _ppFn(name, sig, argNames=Missing):
    if argNames is Missing:
        return f'{name}({", ".join([_ppType(t) for t in sig])})'
    else:
        return f'{name}({", ".join([f"{n}:{_ppType(t)}" for t, n in zip(sig, argNames)])})'

def _ppType(t):
    if t is py:
        return "py"
    elif type(t) is type:
        return t.__name__
    else:
        return repr(t)

def _atPut(xs:list, os:list, ys:list) -> list:
    xs = list(xs)       # immutable
    for fromI, toI in enumerate(os):
        xs[toI] = ys[fromI]
    return xs

def _prettyForm(p):
    style = p.dispatcher.style
    partialClass = p.dispatcher.partialCls
    if style is nullary:
        return f'{style}()'
    else:
        return \
            (f'x >> {style}' if partialClass.numLeft > 0 else f'{style}') + \
            (' >> y' if partialClass.numRight == 1 else '') + \
            (' >> y >> z' if partialClass.numRight == 2 else '')

def _isType(x, out):
    if isinstance(x, (type, BType)):
        return True
    else:
        out['hasValue'] = True
        return False

def _typeOf(x):
    if hasattr(x, '_t'):
        return x._t                             # it's a tv of some sort so return the t
    else:
        t = type(x)
        if t is _CoWProxy:
            t = type(x._target)        # return the type of thing being proxied
        return _BonesTByPythonT.get(t, t)       # type python types as their bones equivalent

def _fnContext(fn, callerFnName, newName=Missing):
    fnname = fn.__name__ if newName is Missing else newName
    # go up the stack to the frame where @coppertop is used to find any prior definition (e.g. import) of the function
    frame = inspect.currentframe()  # do not use `frameInfos = inspect.stack(0)` as it is much much slower
    # discard the frames for registerFn and coppertop
    if frame.f_code.co_name == '_fnContext':
        frame = frame.f_back
    if frame.f_code.co_name == callerFnName:
        frame = frame.f_back
    if frame.f_code.co_name == 'coppertop':  # depending on how coppertop was called this may or may not exist
        frame = frame.f_back
    if frame.f_code.co_name == '__ror__':  # e.g. (lambda...) | (T1^T2)
        frame = frame.f_back
    priorDef = frame.f_locals.get(fnname, Missing)
    if priorDef is Missing:
        priorDef = frame.f_globals.get(fnname, Missing)
    if not isinstance(priorDef, MultiFn):
        priorDef = Missing
    bmodule = frame.f_locals.get('BONES_MODULE', Missing)
    if bmodule is Missing:
        bmodule = frame.f_globals.get('BONES_MODULE', Missing)
    # fi_debug = inspect.getframeinfo(frame, context=0)
    pymodule = frame.f_globals.get('__name__', Missing)
    globals__package__ = frame.f_globals.get('__package__', Missing)
    definedInFunction = frame.f_code.co_name != '<module>'
    fnSignature = inspect.signature(fn)
    tRet = fnSignature.return_annotation
    if tRet in _BonesTByPythonT: raise TypeError(f'{bmodule}.{fnname} - illegal return type {tRet}, use {_BonesTByPythonT[tRet]} instead', ErrSite("illegal return type"))
    if tRet == NO_ANNOTATION: tRet = py
    argNames = []
    sig = []
    pass_tByT = False
    for argName, parameter in fnSignature.parameters.items():
        if argName == 'tByT':
            pass_tByT = True
        else:
            if parameter.kind == inspect.Parameter.VAR_POSITIONAL:
                raiseLessPipe(TypeError(f'{bmodule}.{fnname} has *%s' % argName), ErrSite("has VAR_POSITIONAL"))
            elif parameter.kind == inspect.Parameter.VAR_KEYWORD:
                pass
            else:
                if parameter.default == NOT_OPTIONAL:
                    argNames += [argName]
                    tArg = parameter.annotation
                    if tArg in _BonesTByPythonT: raise TypeError(
                        f'{bmodule}.{fnname} - parameter {argName} has an illegal argument type {tArg}, use {_BonesTByPythonT[tArg]} instead',
                        ErrSite("illegal argument type")
                    )
                    if tArg == NO_ANNOTATION: tArg = py
                    sig.append(tArg)
                else:
                    pass
    return bmodule, pymodule, fnname, priorDef, definedInFunction, argNames, sig, tRet, pass_tByT



# public functions


def selectDispatcher(mfOrD, sigCaller):
    # a little faster than going through the call or pipe interface
    d = mfOrD.dispatcher if isinstance(mfOrD, MultiFn) else mfOrD
    if isinstance(d, unary1):
        u1, tByT = _checkDispatcherForU1(sigCaller, d)
        return u1, tByT
    elif isinstance(d, binary2):
        b2, tByT = _checkDispatcherForB2(sigCaller, d)
        return b2, tByT
    elif isinstance(d, _SingleDispatcher):
        sd, tByT = _checkDispatcherForSD(sigCaller, d)
        return sd, tByT
    elif isinstance(d, _MultiDispatcher):
        sd, tByT = _selectDispatcherFromMD(sigCaller, d)
        return sd, tByT
    elif isinstance(d, Partial):
        p = mfOrD
        io = dict(hasValue=False)
        fullArgTypes = list(((arg if _isType(arg, io) else _typeOf(arg)) for arg in p.args)) # list so can replace elements
        for i, iTBC in enumerate(p.iTBC):
            fullArgTypes[iTBC] = sigCaller[i]
        fullArgTypes = builtins.tuple(fullArgTypes)   # needs to be a tuple so can put in dict
        if isinstance(d.dispatcher, _SingleDispatcher):
            sd, tByT = _checkDispatcherForSD(fullArgTypes, d.dispatcher)
            return sd, tByT
        elif isinstance(d.dispatcher, _MultiDispatcher):
            sd, tByT = _selectDispatcherFromMD(fullArgTypes, d.dispatcher)
            return sd, tByT
        else:
            raise ProgrammerError("Unhandled Partial Case", ErrSite("#1"))
    else:
        raise ProgrammerError("Unhandled Case", ErrSite("#2"))


def anon(*args):
    if len(args) == 1:
        name, _t, fn = '<lambda>', Missing, args[0]
    elif len(args) == 2:
        name, _t, fn = '<lambda>', args[0], args[1]
    elif len(args) == 3:
        name, _t, fn = args[0], args[1], args[2]
    else:
        raise TypeError('Wrong number of args passed to anon', ErrSite("#1"))
    bmodule, pymodule, fnname, priorDef, definedInFunction, argNames, sig, tRet, pass_tByT = _fnContext(fn, 'anon', name)
    return _SingleDispatcher(unary_, fnname, DEFAULT_BMODULE_NAME if bmodule is Missing else bmodule, pymodule, unary, fn, False, Missing, _t, Missing, False)


_PartialClassByStyle = {
    nullary : nullary_,
    unary : unary_,
    rau : rau_,
    binary : binary_,
    ternary : ternary_,
    unary1 : unary1_,
    binary2 : binary2_,
}


typeOf = coppertop(style=unary1, newName='typeOf')(_typeOf)


def _sig(x):
    if isinstance(x, _MultiDispatcher):
        answer = []
        for dBySig in x.dBySigByNumArgs:
            for sig, d in dBySig.items():
                argTs = [_ppType(argT) for argT in sig]
                retT = _ppType(d._tRet)
                answer.append(f'({",".join(argTs)})->{retT} <{d.style.name}>  :   in {d.fullname}')
        return answer
    else:
        argTs = [_ppType(argT) for argT in x.sig]
        retT = _ppType(x._tRet)
        return f'({",".join(argTs)})->{retT} <{x.style.name}>  :   in {x.fullname}'

sig = coppertop(style=unary1, newName='sig')(_sig)


def raiseLessPipe(ex, includeMe=True):
    tb = None
    frame = inspect.currentframe()  # do not use `frameInfos = inspect.stack(0)` as it is much much slower
    # discard the frames for add_traceback
    if not includeMe:
        if frame.f_code.co_name == 'raiseLessPipe':
            frame = frame.f_back
    hasPydev = False
    while True:
        try:
            # frame = sys._getframe(depth)
            frame = frame.f_back
            if not frame: break
        except ValueError as e:
            break
        fullname = frame.f_globals['__name__'] + '.' + frame.f_code.co_name
        ignore = ['IPython', 'ipykernel', 'pydevd', 'coppertop.pipe', '_pydev_imps._pydev_execfile', 'tornado', \
                  'runpy', 'asyncio', 'traitlets']
        # print(fullname)
        if not [fullname for i in ignore if fullname.startswith(i)]:
            # print(fullname)
            tb = types.TracebackType(tb, frame, frame.f_lasti, frame.f_lineno)
        if fullname == '__main__.<module>': break

    while True:
        # frame = sys._getframe(depth)
        frame = frame.f_back
        if not frame: break
        fullname = frame.f_globals['__name__'] + '.' + frame.f_code.co_name
        if fullname.startswith("pydevd"):
            hasPydev = True
    if hasPydev:
        raise ex.with_traceback(tb)
    else:
        raise ex from ex.with_traceback(tb)


def _init():
    # easiest way to keep namespace relatively clean
    from bones.lang.metatypes import weaken

    from ribs.types import index, num, count, offset, null, litint, litdec, littxt, txt

    # weaken - i.e. T1 coerces to any of (T2, T3, ...)  - first is default for a Holder
    weaken(litint, (index, offset, num, count))
    weaken(litdec, (num,))
    weaken(type(None), (null, void))
    weaken(littxt, (txt,))


_init()

if hasattr(sys, '_TRACE_IMPORTS') and sys._TRACE_IMPORTS: print(__name__ + ' - done')
