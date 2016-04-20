
from contextlib import closing
from datetime import datetime
from gzip import GzipFile
import email
import io
import re
import sys
import tempfile
import traceback
import urllib2

from exceptions import *

class ListArchive(object):

    #Things to match in pages downloaded from mail-archive.com
    __SUBJECT = "<H1>(?P<subject>.*)</H1>"
    __DATE = "<I>(?P<date>.*)</I>"
    __BODY = "<PRE>(?P<body>.*)</PRE>"

    __subject_re = re.compile(__SUBJECT)
    __date_re = re.compile(__DATE)
    __body_re = re.compile(__BODY, re.DOTALL)

    def __init__(self):
        super(ListArchive, self).__init__()

    def __process_message(self, url):

        print '-----------------------------------------------------------'
        print "Downloading errata from %s " % url
        try:
            with closing(urllib2.urlopen(url)) as f:
                src = f.read()
        except IOError, e:
            print "Failed to open URL %s: %s...bypassing" % (url, e)
            pass

        subject_match = self.__subject_re.search(src)
        date_match = self.__date_re.search(src)
        body_match = self.__body_re.search(src)

        if subject_match is None or date_match is None or body_match is None:
            raise ParseError("Unexpected page format at %s" % url)

        msg = email.Message.Message()
        msg['Subject'] = subject_match.group('subject')
        msg['Date'] = datetime.fromtimestamp(email.utils.mktime_tz(email.utils.parsedate_tz(date_match.group('date'))))
        msg.set_payload(body_match.group('body'))

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
            erratum.references = url + '\n' + erratum.references
            self.publish_erratum(erratum)

    def process_list_messages(self, config):
        if hasattr(config, 'listurl'):
            urlbase = config.listurl
        else:
            urlbase = self.get_list_url(config)

        if urlbase is None:
            print "No URL for mailing list"
            return

        try:
            fromym = datetime.strptime(config.from_date, "%Y-%m")
            toym = datetime.strptime(config.to_date, "%Y-%m")
        except Exception, e:
            print "Unexpected error:", e
            return None

        if fromym > toym:
            d = toym
            toym = fromym
            fromym = d

        if toym > datetime.today().replace(day=1):
            toym = datetime.today().replace(day=1)

        errata = []
        while fromym <= toym:
            src = None

            if config.use_list_digest:
                try:
                    url = urlbase + '/' + fromym.strftime("%Y-%B.txt.gz")

                    print '-----------------------------------------------------------'
                    print "Downloading errata from %s " % url

                    src = tempfile.NamedTemporaryFile()
                    with closing(urllib2.urlopen(url)) as f:
                        src.write(GzipFile(fileobj=io.BytesIO(f.read())).read())
                except Exception, e:
                    print "Failed to open URL %s: %s...bypassing" % (url, e)
                    pass

                if src is not None:
                    self.process_file_messages(self.config, src.name)
                    src.close()
            else:
                try:
                    url = urlbase + '/' + fromym.strftime("%Y-%B/")

                    print '-----------------------------------------------------------'
                    print "Downloading errata from %s " % url

                    with closing(urllib2.urlopen(url)) as f:
                        src = f.read()
                except Exception, e:
                    print "Failed to open URL %s: %s...bypassing" % (url, e)
                    pass

                if src is not None:
                    for href in re.findall('\d+.html', src):
                        self.__process_message(url + href)

            fromym = fromym.replace(year = fromym.year + ((fromym.month == 12) * 1),
                                    month = (fromym.month % 12) + 1)
