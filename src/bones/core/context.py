# **********************************************************************************************************************
#
#                             Copyright (c) 2019-2022 David Briant. All rights reserved.
#
# **********************************************************************************************************************

import sys
from contextlib import contextmanager as _contextmanager
from bones.core.sentinels import Missing
from bones.core.errors import ProgrammerError

if not hasattr(sys, '_ContextStack'):
    sys._ContextStack = {}



# **********************************************************************************************************************
# context
# **********************************************************************************************************************

class _Context(object):

    def __call__(self, *args, **kwargs):
        if args:
            if len(args) > 1: raise ProgrammerError(f'Can only get one context value at a time, but {args} was requested')
            # get context

        else:
            return _setContext(**kwargs)

    def __getattr__(self, name):
        return sys._ContextStack.get(name, [Missing])[-1]


@_contextmanager
def _setContext(*args, **kwargs):
    # push context
    for k, v in kwargs.items():
        sys._ContextStack.setdefault(k, []).append(v)
    answer = None
    try:
        yield answer
    finally:
        # pop context, deleting if empty
        for k in kwargs.keys():
            sys._ContextStack[k] = sys._ContextStack[k][:-1]
            if len(sys._ContextStack[k]) == 0:
                del sys._ContextStack[k]

context = _Context()