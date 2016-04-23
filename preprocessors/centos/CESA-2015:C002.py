
from classes.preprocessor import *

class Preprocessor(PreprocessorBase):

    def run(self, subject, msg):
        if subject.startswith("[CentOS-announce] CESA-2015:C002"):
            del msg["subject"]
            msg["subject"] = subject.replace("CentOS-7", "CentOS 7")
            return PROCESSED

        return CONTINUE
