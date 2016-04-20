
from classes.preprocessor import *

class Preprocessor(PreprocessorBase):
    def run(self, subject, msg):

        if subject.startswith("[CentOS-announce] CESA-2014:1008 Important CentOS 6"):
            del msg['subject']
            msg['subject'] = subject.replace("CentOS 6", "CentOS 7")
            return PROCESSED

        if subject.startswith("[CentOS-announce] CESA-2014:1008 Important CentOS 7"):
            return DROP

        return CONTINUE

