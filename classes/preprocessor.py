
import email
import re

from log import *
from moduleloader import *

# Preprocessor return values
PROCESSED = 0           # message was handled by the preprocessor
DROP = 1                # message should be ignored
CONTINUE = 2            # continue to the next preprocessor

class Preprocessors(ModuleLoader):

    def __init__(self):
        super(Preprocessors, self).__init__()

    def load_preprocessors(self, type):
        self.load_modules("Preprocessor", "preprocessors", type)

    def preprocess_message(self, msg):
        subject = msg["Subject"]

        if subject is None:
            return None

        subject = re.sub("\s+", " ", subject)
        del msg["Subject"]
        msg["Subject"] = subject

        INFO("-----------------------------------------------------------")
        INFO("processing: %s", subject)

        for pp in self.get_modules():
            rc = pp.run(subject, msg)
            if rc ==  DROP:
                WARN("Preprocessor '%s' dropped message: %s", pp.module_name, subject)
                return None
            if rc ==  PROCESSED:
                INFO("Preprocessor '%s' processed message: %s", pp.module_name, subject)
                break

        return self.process_message(msg)

class PreprocessorBase(Module):
    def __init__(self, name):
        super(PreprocessorBase, self).__init__(name)

