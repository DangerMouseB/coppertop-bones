# **********************************************************************************************************************
#
#                             Copyright (c) 2021-2022 David Briant. All rights reserved.
#
# **********************************************************************************************************************

import sys
sys._TRACE_IMPORTS = True
if hasattr(sys, '_TRACE_IMPORTS') and sys._TRACE_IMPORTS: print(__name__)


# coppertop tests
import coppertop.tests.test_all

# dm tests
import dm.core.tests.test_all
import dm.examples.ex_all
import dm.tests.test_all



def main():
    # coppertop
    coppertop.tests.test_all.main()

    # dm
    dm.core.tests.test_all.main()
    dm.examples.ex_all.main()
    dm.tests.test_all.main()


if __name__ == '__main__':
    main()
    print('pass')
    from bones.lang.metatypes import BType
    from dm.core import count
    from coppertop.core import Missing
    print([t for t in BType._BTypeById if t is not Missing] >> count)

