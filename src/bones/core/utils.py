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
