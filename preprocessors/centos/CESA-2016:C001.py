
from classes.preprocessor import *

class Preprocessor(PreprocessorBase):
    def run(self, subject, msg):

        if not subject.startswith("[CentOS-announce] CESA-2016:C001"):
            return CONTINUE

        del msg["subject"]
        msg["subject"] = subject.replace("ipa and glusterfs", "CentOS 7 ipa/glusterfs")

        msg.set_payload(msg.get_payload().replace("2016:C001", "2016:C001 Important"))

        return PROCESSED
