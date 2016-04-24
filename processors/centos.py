
from contextlib import closing
import bz2
import re
import urllib2
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

from classes.erratum import *
from classes.log import *
from classes.processor import *

class Oval(object):

    _id_re = re.compile('.*-(\d+):(\d+)')

    def __init__(self):
        super(Oval, self).__init__()
        self.__true = None

    def load(self, url):
        INFO("Loading OVAL file")
        with closing(urllib2.urlopen(url)) as f:
            raw = f.read()
            if url.endswith(".bz2"):
                raw = bz2.decompress(raw)
            match = re.search("<definitions>.*</definitions>", raw, re.DOTALL)
            self.__tree = ET.fromstring(match.group(0))

    def supplement(self, erratum):
        if not erratum.advisory_name.startswith("CESA") or self.__tree is None:
            return

        id = self._id_re.sub('\g<1>\g<2>', erratum.advisory_name)
        md = self.__tree.find("./definition/[@id='oval:com.redhat.rhsa:def:{0}']/metadata".format(id))
        if md is None:
            return

        erratum.description = md.find("description").text

        for ref in md.findall("reference"):
            erratum.references += "{0}\n".format(ref.get("ref_url"))

        av = md.find("advisory")
        erratum.issue_date = datetime.strptime(av.find("issued").get("date"), "%Y-%m-%d")
        erratum.update_date = datetime.strptime(av.find("updated").get("date"), "%Y-%m-%d")
        erratum.notes += "\nOVAL Information {0}".format(av.find("rights").text)
        for cve in av.findall("cve"):
            erratum.cves.append(cve.text)

class CentosMessageParser(object):

    __SUBJECT = "\[CentOS-announce\] (CESA|CEBA|CEEA).*CentOS\s+(?P<version>\d)\s+(?P<package>\S+)\s+"
    __ID = r"^CentOS Errata and (?P<type>(Security|Bugfix|BugFix|Enhancement)) Advisory (?P<year>\d{4,4})(:|-)(?P<id>([A-Z]\d{3,3}|\d{4,4}))\s+(?P<severity>.*?)$"
    __UPSTREAM = r"^Upstream details at : .*?(?P<url>.*?)$"
    __URL = r".*?>(?P<url>.*?)<"

    __PKGS = r"^Upstream details.*?\n^(?P<pkgs>.*)^--"
    __ARCH = r"^(?P<arch>\S+?):\s(?P<pkgs>.*?)\n\n"
    __PKG  = r"^(?P<sum>\S+?)\s+(?P<pkg>\S+?).rpm$"

    __subject_re = re.compile(__SUBJECT)
    __id_re = re.compile(__ID, re.DOTALL | re.MULTILINE)
    __upstream_re = re.compile(__UPSTREAM, re.DOTALL | re.MULTILINE)
    __url_re = re.compile(__URL)
    __pkgs_re = re.compile(__PKGS, re.DOTALL | re.MULTILINE)
    __arch_re = re.compile(__ARCH, re.DOTALL | re.MULTILINE)
    __pkg_re = re.compile(__PKG, re.DOTALL | re.MULTILINE)

    def __init__(self):
        return

    def __process_body(self, msg, erratum):
        body = msg.get_payload()

        match = self.__id_re.search(body)
        if match is None:
            return False

        erratum.errata_type = {
                               "Security": Erratum.SECURITY,
                               "Bugfix": Erratum.BUGFIX,
                               "BugFix": Erratum.BUGFIX,
                               "Enhancement": Erratum.ENHANCEMENT
                              }[match.group("type")]
        erratum.advisory_name = "CE{0}A-{1}:{2}".format(match.group("type")[0],
                                                        match.group("year"),
                                                        match.group("id"))
        erratum.synopsis = "{0} {1} Update".format(erratum._package_name,
                                                   match.group("type"))
        if erratum.errata_type == Erratum.SECURITY:
            erratum.synopsis = "{0}: {1}".format(match.group("severity"),
                                                 erratum.synopsis)

        match = self.__upstream_re.search(body)
        if match is None:
            return False

        erratum.topic = match.group("url")
        match = self.__url_re.search(erratum.topic)
        if match is not None:
            erratum.topic = match.group("url")

        match = self.__pkgs_re.search(body)
        if match is None:
            return False

        for match in self.__arch_re.finditer(match.group("pkgs")):
            arch = match.group("arch")
            for match in self.__pkg_re.finditer(match.group("pkgs")):
                erratum.add_package(arch, match.group("pkg"))

        erratum.issue_date = msg.get("Date")
        erratum.product = "CentoOS"
        erratum.description = "Automatically imported CentOS erratum"
        erratum.solution = "Install the associated packages"
        erratum.notes = "Errata announced by CentOS on {0}\n".format(erratum.issue_date.strftime("%Y-%m-%d"))

        self.oval.supplement(erratum)

        return True

    def __process_subject(self, msg, erratum):
        subject_match = self.__subject_re.match(msg["Subject"])

        if subject_match is None:
            return False

        erratum._product_version = subject_match.group("version")
        erratum._package_name = subject_match.group("package")

        return True

    def process_message(self, msg):
        erratum = Erratum()

        if not self.__process_subject(msg, erratum):
            ERROR("Message doesn't appear to be an advisory: {0}", msg["Subject"])
            return None

        if hasattr(self.config, "versions"):
            if erratum._product_version not in self.config.versions.split(","):
                INFO("Version '{0}' not applicable", erratum._product_version)
                return None

        if not self.__process_body(msg, erratum):
            ERROR("Message doesn't appear to be an advisory: {0}", msg["Subject"])
            return None

        return erratum

class Processor(ProcessorBase, CentosMessageParser):

    __LISTURL = "https://lists.centos.org/pipermail/centos-announce"

    def get_list_url(self, config):
        return self.__LISTURL

    def add_command_arguments(self, parser):
        parser.add_argument("--centos-versions", dest="versions", type=str,
                           help=_("Limit processing to comma separated version numbers"))
        parser.add_argument("--oval", dest="oval", type=str,
                           help=_("Path to optional OVAL file"))

    def process(self, config):
        self.oval = Oval()
        if config.oval is not None and config.oval != "":
            self.oval.load(config.oval)

        super(Processor, self).process(config)

