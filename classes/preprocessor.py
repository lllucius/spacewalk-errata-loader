
import email
import imp
import os
import re

# Preprocessor return values
PROCESSED = 0           # message was handled by the preprocessor
DROP = 1                # message should be ignored
CONTINUE = 2            # continue to the next preprocessor

class Preprocessors(object):

    def __init__(self):
        super(Preprocessors, self).__init__()
        self.__objs = []

    def load_preprocessors(self, type):

        path = os.path.dirname(os.path.realpath(__file__))
        path = os.path.realpath(os.path.join(path, "..", "preprocessors", type))
        if os.path.isdir(path):
            for pp in sorted(os.listdir(path)):
                if pp.endswith(".py") and pp != "__init__.py":
                    name = pp.split(".")[0]
                    info = imp.find_module(name, [ path ])
                    if info is not None:
                        try:
                            module = imp.load_module(name, *info)
                            klass = getattr(module, "Preprocessor")
                            self.__objs.append(klass(name))
                        finally:
                            info[0].close()

    def preprocess_message(self, msg):
        subject = msg['Subject']

        if subject is None:
            return None

        subject = re.sub('\s+', ' ', subject)
        del msg['Subject']
        msg['Subject'] = subject

        for pp in self.__objs:
            rc = pp.run(subject, msg)
            if rc ==  DROP:
                print "Preprocessor '%s' dropped message:" % pp.name
                print subject
                return None
            if rc ==  PROCESSED:
                print "Preprocessor '%s' processed message:" % pp.name
                print subject
                break

        return self.process_message(msg)

class PreprocessorBase:
    def __init__(self, name):
        self.name = name

    def get_name(self):
        return self.name


