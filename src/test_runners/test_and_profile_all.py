# **********************************************************************************************************************
#
#                             Copyright (c) 2021 David Briant. All rights reserved.
#
# **********************************************************************************************************************

import sys
sys._TRACE_IMPORTS = True
if hasattr(sys, '_TRACE_IMPORTS') and sys._TRACE_IMPORTS: print(__name__)

import coppertop.pipe

import cProfile, pstats
cProfile.run('''

import coppertop.tests.test_all

''', 'testAndProfileAll.profile')

from pstats import SortKey
p = pstats.Stats('test_and_profile_all.profile')
p.strip_dirs().sort_stats(SortKey.CUMULATIVE).print_stats(30)



def main():
    coppertop.tests.testAll.main()


if __name__ == '__main__':
    main()
    print('pass')
