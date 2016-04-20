
from datetime import datetime

class Erratum(object):

    SECURITY = 'Security Advisory'
    ENHANCEMENT = 'Product Enhancement Advisory'
    BUGFIX = 'Bug Fix Advisory'

    def __init__(self):
        self.synopsis = None
        self.advisory_name = None
        self.advisory_release = 1
        self.advisory_type = Erratum.SECURITY
        self.product = None
        self.errataFrom = "" #None
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

        #This is used internally by the script
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
                'synopsis': self.synopsis,
                'advisory_name': self.advisory_name,
                'advisory_release': self.advisory_release,
                'advisory_type': self.advisory_type,
                'product': self.product,
                'errataFrom': self.errataFrom,
                'topic': self.topic,
                'description': self.description,
                'references': self.references,
                'notes': self.notes,
                'solution': self.solution
               }

    def is_valid(self):
        info = self.get_info_dict()

        required = [
                    'synopsis',
                    'advisory_name',
                    'advisory_release',
                    'advisory_type',
                    'product',
                    'topic',
                    'description',
                    'solution'
                   ]

        for attr in required:
            if info[attr] is None:
                print "Erratum is missing the '%s':" % attr
                return False

        if self._package_groups is None:
            print "No packages added to erratum"
            return False

        for group in self._package_groups:
            if self._package_groups[group] is None:
                print "No packages added to group '%s'" % group
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
            print "Invalid group name %s" % group
            return
        if name not in self._package_groups[group]:
            print "Name %s not in group %s" % (name, group)
            return
        ndx = self._package_groups[group].index(name)
        self._package_groups[group][ndx] = \
            "MISSING: " + self._package_groups[group][ndx]

    def show(self):
        print "%-20s = %s" % ("Synopsis:", self.synopsis)
        print "%-20s = %s" % ("Name:", self.advisory_name)
        print "%-20s = %s" % ("Release:", self.advisory_release)
        print "%-20s = %s" % ("Type:", self.advisory_type)
        print "%-20s = %s" % ("Product:", self.product)
        print "%-20s = %s" % ("From:", self.errataFrom)
        print "%-20s = %s" % ("Topic:", self.topic)
        print "%-20s = %s" % ("Description:", self.description)
        print "%-20s = %s" % ("References:", self.references)
        print "%-20s = %s" % ("Notes:", self.notes)
        print "%-20s = %s" % ("Solution:", self.solution)
        print "%-20s = %s" % ("Issued:", self.issue_date)
        print "%-20s = %s" % ("Updated:", self.update_date)
 
        n = "Keywords:"
        for keyword in self.keywords:
            print "%-20s = %s" % (n, keyword)
            n = ""

        n = "Package IDs:"
        for pkg in self.packages:
            print "%-20s = %s" % (n, pkg)
            n = ""

        n = "Channels:"
        for channel in self.channelLabel:
            print "%-20s = %s" % (n, channel)
            n = ""

        n = "CVEs:"
        for cve in self.cves:
            print "%-20s = %s" % (n, cve)
            n = ""

        print 
        print "%-20s = %s" % ("Version:", self._product_version)
        print "%-20s = %s" % ("Package:", self._package_name)

        print "Package groups:"
        for group in self._package_groups:
            for pkg in self._package_groups[group]:
                print "%-20s = %s" % (group, pkg)
                group = ""

