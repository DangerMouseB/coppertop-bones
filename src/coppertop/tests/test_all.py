# **********************************************************************************************************************
#
#                             Copyright (c) 2021-2022 David Briant. All rights reserved.
#
# **********************************************************************************************************************

import sys
sys._TRACE_IMPORTS = True
if hasattr(sys, '_TRACE_IMPORTS') and sys._TRACE_IMPORTS: print(__name__)


# coppertop tests
import coppertop.tests.test_anon_and_partial
import coppertop.tests.test_misc
import coppertop.tests.test_ns
import coppertop.tests.test_pipeable
import coppertop.tests.test_scope
import coppertop.tests.test_styles
import coppertop.tests.test_testing



def main():
    coppertop.tests.test_anon_and_partial.main()
    coppertop.tests.test_misc.main()
    coppertop.tests.test_ns.main()
    coppertop.tests.test_pipeable.main()
    coppertop.tests.test_scope.main()
    coppertop.tests.test_styles.main()
    coppertop.tests.test_testing.main()


if __name__ == '__main__':
    main()
    print('pass')

