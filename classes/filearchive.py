
import email
import re
import sys
import traceback

from exceptions import *

class FileArchive(object):

    #Split on lines formatted thusly: From kbsingh at centos.org  Thu Jan  8 16:25:09 2009
    __SEPARATOR="From .*[A-Za-z]{3,3} [A-Za-z]{3,3} [ 0-9]{2,2} \d{2,2}:\d{2,2}:\d{2,2} \d{4,4}\n"
    __splitter_re = re.compile(__SEPARATOR)

    def __init__(self):
        super(FileArchive, self).__init__()

    def __process_message(self, src):
        msg = email.message_from_string(src)

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

