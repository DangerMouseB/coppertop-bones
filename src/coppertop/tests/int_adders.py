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

BONES_MODULE = 'tests.adders'

from coppertop.pipe import *
from dm.core.types import index, pylist


@coppertop
def addOne(x:index) -> index:
    return x + 1

# test that functions can be redefined in the same file (and thus same module)
@coppertop
def addOne(x: index) -> index:
    return x + 1

@coppertop
def eachAddOne(xs:pylist) -> pylist:
    answer = []
    for x in xs:
        answer.append(x >> addOne)
    return answer

@coppertop
def addTwo(x:index) -> index:
    return x + 2

@coppertop
def eachAddTwo(xs:pylist) -> pylist:
    answer = []
    for x in xs:
        answer.append(x >> addTwo)
    return answer
