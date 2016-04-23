
import imp
import os

from log import *

class ModuleLoader(object):

    def __init__(self):
        super(ModuleLoader, self).__init__()
        self.__objs = []

    def load_modules(self, classname, topdir, subdir=None):
        path = os.path.dirname(os.path.realpath(__file__))
        path = os.path.join(path, "..", topdir)
        if subdir is not None:
            path = os.path.join(path, subdir)

        if os.path.isdir(path):
            for name in sorted(os.listdir(path)):
                if name.endswith(".py") and name != "__init__.py":
                    name = name.split(".")[0]
                    info = imp.find_module(name, [path])
                    if info is not None:
                        try:
                            module = imp.load_module(name, *info)
                            klass = getattr(module, classname)
                            self.__objs.append(klass(name))
                        finally:
                            info[0].close()

    def get_modules(self):
        return self.__objs

    def get_module(self, name):
        for module in self.__objs:
            if name == module.module_name:
                return module

        return None

    def get_module_names(self):
        names = []
        for module in self.__objs:
            names.append(module.module_name)
        return names

class Module(object):

    module_name = None

    def __init__(self, name):
        super(Module, self).__init__()
        self.module_name = name

