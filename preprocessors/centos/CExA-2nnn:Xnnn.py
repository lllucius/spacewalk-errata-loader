
import re

from classes.preprocessor import *

class Preprocessor(PreprocessorBase):

    def run(self, subject, msg):
        if re.match("\[CentOS-announce\] CE.A-2...\:X...", subject) is None:
            return CONTINUE

        # It wouldn't be too difficult to rearrange the message to
        # match the "normal" format

        return DROP
