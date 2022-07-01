# **********************************************************************************************************************
#
#                             Copyright (c) 2021 David Briant. All rights reserved.
#
# **********************************************************************************************************************

import inspect, types

def raiseLessPipe(ex, includeMe=True):
    tb = None
    frame = inspect.currentframe()  # do not use `frameInfos = inspect.stack(0)` as it is much much slower
    # discard the frames for add_traceback
    if not includeMe:
        if frame.f_code.co_name == 'raiseLessPipe':
            frame = frame.f_back
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
            # print('-------- '+fullname)
            tb = types.TracebackType(tb, frame, frame.f_lasti, frame.f_lineno)
        else:
            pass
            # print(fullname)
        if fullname == '__main__.<module>': break
    hasPydev = False
    hasIPython = False
    while True:
        # frame = sys._getframe(depth)
        frame = frame.f_back
        if not frame: break
        fullname = frame.f_globals['__name__'] + '.' + frame.f_code.co_name
        # print(fullname)
        if fullname.startswith("pydevd"): hasPydev = True
        if fullname.startswith("IPython"): hasIPython = True
    if hasPydev or hasIPython:
        raise ex.with_traceback(tb)
    else:
        raise ex from ex.with_traceback(tb)

def firstKey(d):
    # https://stackoverflow.com/questions/30362391/how-do-you-find-the-first-key-in-a-dictionary
    for k in d:
        return k

def firstValue(d):
    # https://stackoverflow.com/questions/30362391/how-do-you-find-the-first-key-in-a-dictionary
    for v in d.values():
        return v
