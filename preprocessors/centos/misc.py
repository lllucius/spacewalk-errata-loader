
import re

from classes.preprocessor import *

class Preprocessor(PreprocessorBase):

    def run(self, subject, msg):
        if re.match("\[CentOS-announce\] Announcing", subject) is not None:
            return DROP

        if re.match("\[CentOS-announce\] Notice of Service Outage", subject) is not None:
            return DROP


        return CONTINUE
