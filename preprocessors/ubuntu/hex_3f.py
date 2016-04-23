
from classes.preprocessor import *

class Preprocessor(PreprocessorBase):
    def run(self, subject, msg):

        payload = msg.get_payload()
        if chr(63) not in payload:
            return CONTINUE

        msg.set_payload(payload.replace(chr(63), " "))

        return CONTINUE
