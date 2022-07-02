# **********************************************************************************************************************
#
#                             Copyright (c) 2011-2020 David Briant. All rights reserved.
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


import traceback, contextlib
# from io import StringIO


@contextlib.contextmanager
def HookStdOutErrToLines():
    oldout, olderr = sys.stdout, sys.stderr
    try:
        sys.stdout = _StreamToLines()
        sys.stderr = _StreamToLines()
        yield [sys.stdout.lines, sys.stderr.lines]
    finally:
        sys.stdout, sys.stderr = oldout, olderr


class _StreamToLines(object):
    def __init__(self):
        self.lines = []
        self.textBuffer = ""
    def write(self, text=""):
        if len(text) > 0:
            splits = text.split("\n")
            for split in splits[:-1]:
                self.textBuffer += split
                self.lines.append(self.textBuffer)
                self.textBuffer = ""
            self.textBuffer += splits[-1:][0]



class assertRaises(object):

    def __init__(self, expectedExceptionType):
        self.expectedExceptionType = expectedExceptionType
        self.exceptionType = None
        self.exceptionValue = None
        self.tb = None

    def __enter__(self):
        return self

    def __exit__(self, exceptionType, exceptionValue, tb):
        self.exceptionType = exceptionType
        self.exceptionValue = exceptionValue
        self.tb = tb
        if exceptionType is None:
            # no exception was raised
            raise AssertionError("No exception raised, %s expected." % self.expectedExceptionType)        # no error was raised
        elif not issubclass(exceptionType, self.expectedExceptionType):
            # the wrong exception was raised
            # print the tb to make it easier to figure why the test is failing
            traceback.print_tb(tb)
            raise AssertionError("%s raised. %s expected." % (exceptionType, self.expectedExceptionType))
        else:
            # the correct error was raised
            return True


