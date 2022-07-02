# **********************************************************************************************************************
#
#                             Copyright (c) 2011-2012 David Briant. All rights reserved.
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
sys._TRACE_IMPORTS = True


from coppertop.testing import HookStdOutErrToLines, assertRaises


def testStdoutHooker():
    with HookStdOutErrToLines() as outerr:
        lines = outerr[0]
        print("hello")
        assert len(lines) == 1, lines
        assert lines[0] == "hello", lines
        print()
        print("there", "is", "\n", "another line\nagain")
        print()
        assert len(lines) == 6, lines
        assert lines[2] == "there is ", lines
        assert lines[3] == " another line", lines
        assert lines[4] == "again", lines
        assert lines[5] == "", lines


def testAssertRaises():
    
    # test correct error
    with assertRaises(NotImplementedError) as e:
        raise NotImplementedError()
    assert e.exceptionType == NotImplementedError, (e.type, e.e)
    
    # test correct error
    with assertRaises(NotImplementedError) as e:
        raise NotImplementedError
    assert e.exceptionType == NotImplementedError, (e.type, e.e)
    
    # test no error
    try:
        with assertRaises(NotImplementedError) as e:
            pass
    except AssertionError:
        assert e.exceptionType == None, (e.type, e.e)
    except Exception as e:
        assert False, e
    
    # test wrong error
    class Fred(Exception): pass
    try:
        with assertRaises(NotImplementedError) as e:
            raise Fred
    except AssertionError:
        assert e.exceptionType == Fred, (e.exceptionType, e.e)
    except Exception as e:
        assert False, e


def main():
    testStdoutHooker()
    testAssertRaises()


if __name__ == '__main__':
    main()
    print('pass')

