
from datetime import datetime
import email
import gzip
import os
import re
import sys
import traceback

from exceptions import *

class FileArchive(object):

    __SEPARATOR="From .*[A-Za-z]{3,3} [A-Za-z]{3,3} [ 0-9]{2,2} \d{2,2}:\d{2,2}:\d{2,2} \d{4,4}\n"
    __splitter_re = re.compile(__SEPARATOR)

    def __init__(self):
        super(FileArchive, self).__init__()

    def __process_message(self, src):
        msg = email.message_from_string(src)

        date = msg['date']
        del msg['Date']
        msg['Date'] = datetime.fromtimestamp(email.utils.mktime_tz(email.utils.parsedate_tz(date)))

        print '-----------------------------------------------------------'
        print 'processing %s' % msg['Subject']

        erratum = None

        try:
            erratum = self.preprocess_message(msg)
        except ParseInfo, e:
            print e
            pass
        except ParseError, e:
            print "Failed to process message. Reason:"
            print e
            pass
        except Exception, e:
            print "Failed to process message. Reason:"
            print e
            traceback.print_exc(file = sys.stdout)

        if erratum is not None:
            self.publish_erratum(erratum)

    def process_file_messages(self, config, filename):
        errata = []

        print '-----------------------------------------------------------'
        print "Extracting errata from %s " % filename

        if not os.path.exists(filename):
            print "Input file %s does not exist" % filename
            return

        if not os.path.isfile(filename):
            print "Input file %s is not a normal file" % filename
            return

        if not os.access(filename, os.R_OK):
            print "Input file %s is not readable" % filename
            return

        try:
            if filename.endswith('.gz'):
                with gzip.open(filename, 'rb') as f:
                    data = f.read()
            else:
                with open(filename, 'r') as f:
                    data = f.read()
        except Exception, e:
            raise ParseError("reading %s failed: %s" % (filename, e))                

        for src in self.__splitter_re.split(data):
            if len(src):
                self.__process_message(src)

