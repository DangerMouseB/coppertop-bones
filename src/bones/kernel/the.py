# **********************************************************************************************************************
#
#                             Copyright (c) 2019-2021 David Briant. All rights reserved.
#
# **********************************************************************************************************************


from bones.core.sentinels import Missing
from bones.lang.types import unary

# keep the contexts on the kernel to relieve the burden of type memory management from the storage manager

class Kernel(object):
    def __init__(self, sm):
        self.ctxs = {}
        self.sm = sm
        self.modByPath = {}
        self.styleByName = {}

    def styleForName(self, name):
        return self.styleByName.get(name, unary)

    def loadModules(self, paths):
        # i.e. searches PYTHON_PATH and BONES_PATH for bones/ex/ and load core.py or core.b
        for path in paths:
            root = __import__(path)
            names = path.split(".")
            modPath = names[0]
            mod = root
            if modPath not in self.modByPath:
                self.modByPath[modPath] = mod
            for name in names[1:]:
                modPath = modPath + '.' + name if modPath else name
                if modPath not in self.modByPath:
                    mod = getattr(mod, name)
                    self.modByPath[modPath] = mod


kernelForCoppertop = Kernel(Missing)
