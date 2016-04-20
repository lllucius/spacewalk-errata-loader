
import re

from classes.erratum import *
from classes.exceptions import *
from classes.processor import *

class CentosMessageParser(object):

    __SUBJECT = "\[CentOS-announce\] (CESA|CEBA|CEEA).*CentOS\s+(?P<version>\d)\s+(?P<package>\S+)\s+"
    __ID = r"^CentOS Errata and (?P<type>(Security|Bugfix|BugFix|Enhancement)) Advisory (?P<year>\d{4,4})(:|-)(?P<id>([A-Z]\d{3,3}|\d{4,4}))\s+(?P<severity>.*?)$"
    __UPSTREAM = r"^Upstream details at : .*?>(?P<url>.*?)<"

    __PKGS = r"^Upstream details.*?\n^(?P<pkgs>.*)^--"
    __ARCH = r"^(?P<arch>\S+?):\s(?P<pkgs>.*?)\n\n"
    __PKG  = r"^(?P<sum>\S+?)\s+(?P<pkg>\S+?).rpm$"

    __subject_re = re.compile(__SUBJECT)
    __id_re = re.compile(__ID, re.DOTALL | re.MULTILINE)
    __upstream_re = re.compile(__UPSTREAM, re.DOTALL | re.MULTILINE)
    __pkgs_re = re.compile(__PKGS, re.DOTALL | re.MULTILINE)
    __arch_re = re.compile(__ARCH, re.DOTALL | re.MULTILINE)
    __pkg_re = re.compile(__PKG, re.DOTALL | re.MULTILINE)

    def __init__(self):
        return

    def __process_body(self, msg, erratum):
        body = msg.get_payload()

        match = self.__id_re.search(body)
        if match is None:
            raise ParseError("Message doesn't appear to be an advisory")
        erratum.errata_type = {'Security': Erratum.SECURITY,
                               'Bugfix': Erratum.BUGFIX,
                               'BugFix': Erratum.BUGFIX,
                               'Enhancement': Erratum.ENHANCEMENT
                                }[match.group('type')]
        erratum.advisory_name = 'CE%sA-%s:%s' % (match.group('type')[0],
                                                 match.group('year'),
                                                 match.group('id'))
        erratum.synopsis = '%s %s Update' % (erratum._package_name,
                                             match.group('type'))
        if erratum.errata_type ==  Erratum.SECURITY:
            erratum.synopsis = '%s: %s' % (match.group('severity'),
                                           erratum.synopsis)

        match = self.__upstream_re.search(body)
        if match is None:
            raise ParseError("Message doesn't appear to be an advisory")
        erratum.topic = match.group('url')

        match = self.__pkgs_re.search(body)
        if match is None:
            raise ParseError("Message doesn't appear to be an advisory")
        for match in self.__arch_re.finditer(match.group('pkgs')):
            arch = match.group('arch')
            for match in self.__pkg_re.finditer(match.group('pkgs')):
                erratum.add_package(arch, match.group('pkg'))

        erratum.product = "CentoOS"
        erratum.description = 'Automatically imported CentOS erratum'
        erratum.solution = 'Install the associated packages'
        erratum.notes = "Errata announced by CentOS on " + erratum.issue_date.strftime("%Y-%m-%d")

    #Construct the basic details about the errata from the message subject
    def __process_subject(self, msg, erratum):

        subject_match = self.__subject_re.match(msg['Subject'])

        if subject_match is None:
            raise ParseError("Message doesn't appear to be an advisory")

        erratum._product_version = subject_match.group('version')
        erratum._package_name = subject_match.group('package')

    def process_message(self, msg):

        erratum = Erratum()
        erratum.issue_date = msg.get("Date")

        self.__process_subject(msg, erratum)
        self.__process_body(msg, erratum)

        return erratum

class CentosProcessor(Processor, CentosMessageParser):

    __LISTURL = "https://lists.centos.org/pipermail/centos-announce"

    @staticmethod
    def add_command_arguments(parser):
        pass

    def __init__(self):
        super(CentosProcessor, self).__init__()

    def get_list_url(self, config):
        return self.__LISTURL

