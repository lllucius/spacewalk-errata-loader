
from datetime import datetime
import re

from classes.erratum import *
from classes.log import *
from classes.processor import *

class UbuntuMessageParser(object):
    __SUBJECT = r"\[USN-(?P<id>\d+-\d+)\] (?P<other>.*)"

    __ID      = r"Ubuntu Security Notice\s(?P<id>.*?)\s(?P<issued>.*)\s"
    __TOPIC   = r"=\n\n(?P<topic>.*?)\s+Summary:"
    __PRODUCT = r"- (?P<product>.*?) (?P<version>.*?)\s(?P<other>.*?)Summary:"
    __SUMMARY = r"Summary:\s*?(?P<summary>\S.*)\s*?Software Description:"
    __DETAILS = r"Details:\s*?(?P<details>\S.*)Update instructions:"
    __UPDATE  = r"Update instructions:\s*?(?P<update>\S.*)References:"
    __REFS    = r"References:\s*?(?P<references>\S.*)Package Information:"
    __CVES    = "(?P<cve>CVE-\d{4}-\d{4})"

    __PKGS = r":\s+(?P<pkgs>.*)"
    __ARCH = r"^(?P<arch>.*?):\s(?P<pkgs>.*?)\n\n"
    __PKG  = r"^\s\s(?P<pkg>\S+?)\s+(?P<ver>\S+?)$"

    __subject_re = re.compile(__SUBJECT)

    __id_re      = re.compile(__ID)
    __topic_re   = re.compile(__TOPIC, re.DOTALL)
    __product_re = re.compile(__PRODUCT, re.DOTALL)
    __summary_re = re.compile(__SUMMARY, re.DOTALL)
    __details_re = re.compile(__DETAILS, re.DOTALL)
    __update_re = re.compile(__UPDATE, re.DOTALL)
    __refs_re = re.compile(__REFS, re.DOTALL)
    __cves_re = re.compile(__CVES, re.DOTALL)
    __pkgs_re = re.compile(__PKGS, re.DOTALL)
    __arch_re = re.compile(__ARCH, re.DOTALL | re.MULTILINE)
    __pkg_re = re.compile(__PKG, re.MULTILINE)

    def __process_body(self, msg, erratum):
        body = msg.get_payload()

        if body.find("reboot your computer") != -1:
            erratum.keywords.append("reboot_suggested")

        match = self.__id_re.search(body)
        if match is None:
            ERROR("Message doesn't appear to be an advisory")
            return False

        erratum.advisory_name = match.group("id")
        erratum.issue_date = datetime.strptime(match.group("issued"), "%B %d, %Y")

        match = self.__topic_re.search(body)
        if match is None:
            ERROR("Message doesn't appear to be an advisory")
            return False

        erratum.topic = match.group("topic")

        match = self.__summary_re.search(body)
        if match is None:
            ERROR("Message doesn't appear to be an advisory")
            return False

        erratum.synopsis = re.sub("\s+", " ", match.group("summary"))

        erratum.product = "Ubuntu"

        match = self.__details_re.search(body)
        if match is None:
            ERROR("Message doesn't appear to be an advisory")
            return False

        erratum.description = match.group("details")

        match = self.__update_re.search(body)
        if match is None:
            ERROR("Message doesn't appear to be an advisory")
            return False

        erratum.solution = match.group("update")

        match = self.__refs_re.search(body)
        if match is None:
            ERROR("Message doesn't appear to be an advisory")
            return False

        erratum.references = match.group("references")

        match = self.__cves_re.findall(erratum.references)
        if match is None:
            ERROR("Message doesn't appear to be an advisory")
            return False

        erratum.cves = match

        match = self.__pkgs_re.search(erratum.solution)
        if match is None:
            ERROR("Message doesn't appear to be an advisory")
            return False

        for match in self.__arch_re.finditer(match.group("pkgs")):
            arch = match.group("arch")
            for match in self.__pkg_re.finditer(match.group("pkgs")):
                erratum.add_package(arch, match.group("pkg") + "-" + match.group("ver"))

        return True

    def __process_subject(self, msg, erratum):
        subject = msg.get("Subject")

        match = self.__subject_re.match(subject)

        if match is None:
            ERROR("Message doesn't appear to be an advisory")
            return False

        erratum._id = match.group("id")
        erratum.synopsis = match.group("other")

        return True

    def process_message(self, msg):

        erratum = Erratum()

        if not self.__process_subject(msg, erratum):
            return None

        if not self.__process_body(msg, erratum):
            return None

        return erratum

class Processor(ProcessorBase, UbuntuMessageParser):

    __LISTURL = "https://lists.ubuntu.com/archives/ubuntu-security-announce"

    def get_list_url(self, config):
        return self.__LISTURL

