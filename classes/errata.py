
from log import *

class Errata(object):
    def __init__(self):
        super(Errata, self).__init__()
        self.__cache = {}

    def init_errata_cache(self):
        INFO("Loading errata cache")
        channels = self.channel_list_software_channels()
        for channel in channels:
            errata = self.software_list_errata(channel["label"])
            for erratum in errata:
                self.__cache[erratum["advisory_name"]] = erratum["id"]

    def add_erratum_to_cache(self, erratum, id):
        self.__cache[erratum.advisory_name] = id

    def is_erratum_in_cache(self, erratum):
        return erratum.advisory_name in self.__cache

    def publish_erratum(self, erratum):
        if not erratum.is_valid():
            return

        if self.is_erratum_in_cache(erratum):
            WARN("Erratum '%s' already exists", erratum.advisory_name)
            return

        groups = erratum.get_groups()
        channels = self.get_channels()
        for group in groups:
            for channel in channels:
                found = []
                names = groups[group]
                for name in names:
                    pkgid = self.get_package_id(channel, name)
                    if pkgid is not None:
                        erratum.add_package_id(pkgid)
                        found.append(name)

                missing = []
                valid = True
                for name in names:
                    if name not in found:
                        missing.append(name)
                        erratum.set_missing(group, name)
                        valid = False
                if valid:
                    erratum.add_channel(channel)
                else:
                    allmissing = len(names) == len(missing)
                    if self.config.report_missing:
                        if (not allmissing) or \
                           (allmissing and not self.config.suppress_missing_group):
                            for name in missing:
                                WARN("missing %s from %s", name, group)
                    if self.config.publish_with_missing and not allmissing:
                        erratum.add_channel(channel)

        if len(erratum.packages) == 0:
            WARN("All packages missing for Erratum %s", erratum.advisory_name)
            return

        if len(erratum.channelLabel) == 0:
            WARN("Erratum not assigned to any channels")
            return

        id = self.errata_create(erratum)["id"]
        self.add_erratum_to_cache(erratum, id)

        details = {
                   "issue_date": erratum.issue_date,
                   "update_date": erratum.update_date,
                   "cves": erratum.cves,
                  }
        self.errata_set_details(erratum, details)

        INFO("Published %s", erratum.advisory_name)

        return

