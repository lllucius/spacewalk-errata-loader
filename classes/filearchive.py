
from datetime import datetime
import email
import gzip
import os
import re

from log import *

class FileArchive(object):

    __SEPARATOR="From .*[A-Za-z]{3,3} [A-Za-z]{3,3} [ 0-9]{2,2} \d{2,2}:\d{2,2}:\d{2,2} \d{4,4}\n"
    __splitter_re = re.compile(__SEPARATOR)

    def __init__(self):
        super(FileArchive, self).__init__()

    def __process_message(self, src):
        self.errata_processed += 1
        if self.errata_processed > self.config.max_errata:
            ERROR("Maximum number of errata (%s) processed", self.config.max_errata)
            return

        msg = email.message_from_string(src)

        date = msg["Date"]
        del msg["Date"]
        msg["Date"] = datetime.fromtimestamp(email.utils.mktime_tz(email.utils.parsedate_tz(date)))

        erratum = self.preprocess_message(msg)

        if erratum is not None:
            self.publish_erratum(erratum)

    def process_file_messages(self, config, filename):
        errata = []

        INFO("-----------------------------------------------------------")
        INFO("Extracting errata from %s", filename)

        if not os.path.exists(filename):
            ERROR("Input file %s does not exist", filename)
            return

        if not os.path.isfile(filename):
            ERROR("Input file %s is not a normal file", filename)
            return

        if not os.access(filename, os.R_OK):
            ERROR("Input file %s is not readable", filename)
            return

        if filename.endswith(".gz"):
            with gzip.open(filename, "rb") as f:
                data = f.read()
        else:
            with open(filename, "r") as f:
                data = f.read()

        for src in self.__splitter_re.split(data):
            if len(src):
                self.__process_message(src)

