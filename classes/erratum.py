
from datetime import datetime

from log import *

class Erratum(object):

    SECURITY = "Security Advisory"
    ENHANCEMENT = "Product Enhancement Advisory"
    BUGFIX = "Bug Fix Advisory"

    def __init__(self):
        self.synopsis = None
        self.advisory_name = None
        self.advisory_release = 1
        self.advisory_type = Erratum.SECURITY
        self.product = None
        self.errataFrom = ""
        self.topic = None
        self.description = None
        self.references = ""
        self.notes = ""
        self.solution = None

        self.bugs = []
        self.keywords = []
        self.packages = []

        self.publish = True

        self.channelLabel = []
        self.cves = []

        self.issue_date = datetime.now()
        self.update_date = datetime.now()

        self._product_version = 0
        self._package_name = ""
        self._package_groups = {}

    def __trunc(self, value):
        if value is not None and len(value) > 4000:
            msg = "\nLimiited to 4000 characters, refer to original for full text."
            value = value[:(4000 - len(msg))] + msg

        return value

    @property
    def synopsis(self):
        return self.__synopsis

    @synopsis.setter
    def synopsis(self, value):
        self.__synopsis = self.__trunc(value)

    @property
    def topic(self):
        return self.__topic

    @topic.setter
    def topic(self, value):
        self.__topic = self.__trunc(value)

    @property
    def description(self):
        return self.__description

    @description.setter
    def description(self, value):
        self.__description = self.__trunc(value)

    @property
    def notes(self):
        return self.__notes

    @notes.setter
    def notes(self, value):
        self.__notes = self.__trunc(value)

    @property
    def references(self):
        return self.__references

    @references.setter
    def references(self, value):
        self.__references = self.__trunc(value)

    @property
    def solution(self):
        return self.__solution

    @solution.setter
    def solution(self, value):
        self.__solution = self.__trunc(value)


    def get_package_ids(self):
        return self.packages

    def get_info_dict(self):
        return {
                "synopsis": self.synopsis,
                "advisory_name": self.advisory_name,
                "advisory_release": self.advisory_release,
                "advisory_type": self.advisory_type,
                "product": self.product,
                "errataFrom": self.errataFrom,
                "topic": self.topic,
                "description": self.description,
                "references": self.references,
                "notes": self.notes,
                "solution": self.solution
               }

    def is_valid(self):
        info = self.get_info_dict()

        required = [
                    "synopsis",
                    "advisory_name",
                    "advisory_release",
                    "advisory_type",
                    "product",
                    "topic",
                    "description",
                    "solution"
                   ]

        for attr in required:
            if info[attr] is None:
                ERROR("Erratum is missing the '{0}'", attr)
                return False

        if self._package_groups is None:
            ERROR("No packages added to erratum")
            return False

        for group in self._package_groups:
            if self._package_groups[group] is None:
                ERROR("No packages added to group '{0}'", group)
                return False

        return True

    def add_package(self, group, pkg):
        if group not in self._package_groups:
            self._package_groups[group] = []
        self._package_groups[group].append(pkg)

    def add_channel(self, channel):
        self.channelLabel.append(channel)

    def add_package_id(self, pkgid):
        self.packages.append(pkgid)

    def get_groups(self):
        return self._package_groups

    def set_missing(self, group, name):
        if group not in self._package_groups:
            CRITICAL("Invalid group name {0}", group)
            return
        if name not in self._package_groups[group]:
            CRITICAL("Name {0} not in group {1}", name, group)
            return
        ndx = self._package_groups[group].index(name)
        self._package_groups[group][ndx] = \
            _("MISSING: ") + self._package_groups[group][ndx]

    def show(self):
        INFO("{0:<20} = {1}", _("Synopsis:"), self.synopsis)
        INFO("{0:<20} = {1}", _("Name:"), self.advisory_name)
        INFO("{0:<20} = {1}", _("Release:"), self.advisory_release)
        INFO("{0:<20} = {1}", _("Type:"), self.advisory_type)
        INFO("{0:<20} = {1}", _("Product:"), self.product)
        INFO("{0:<20} = {1}", _("From:"), self.errataFrom)
        INFO("{0:<20} = {1}", _("Topic:"), self.topic)
        INFO("{0:<20} = {1}", _("Description:"), self.description)
        INFO("{0:<20} = {1}", _("References:"), self.references)
        INFO("{0:<20} = {1}", _("Notes:"), self.notes)
        INFO("{0:<20} = {1}", _("Solution:"), self.solution)
        INFO("{0:<20} = {1}", _("Issued:"), self.issue_date)
        INFO("{0:<20} = {1}", _("Updated:"), self.update_date)

        n = _("Keywords:")
        for keyword in self.keywords:
            INFO("{0:<20} = {1}", n, keyword)
            n = ""

        n = _("Package IDs:")
        for pkg in self.packages:
            INFO("{0:<20} = {1}", n, pkg)
            n = ""

        n = _("Channels:")
        for channel in self.channelLabel:
            INFO("{0:<20} = {1}", n, channel)
            n = ""

        n = _("CVEs:")
        for cve in self.cves:
            INFO("{0:<20} = {1}", n, cve)
            n = ""

        INFO(" ")
        INFO("{0:<20} = {1}", _("Version:"), self._product_version)
        INFO("{0:<20} = {1}", _("Package:"), self._package_name)

        INFO("Package groups:")
        for group in self._package_groups:
            for pkg in self._package_groups[group]:
                INFO("{0:<20} = {1}", group, pkg)
                group = ""

