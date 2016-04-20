
import re

class Packages(object):

    __escape_re = re.compile(r'([\+\-\&\|\!\(\)\{\}\[\]\^\"\~\*\?\:\\])')

    def __init__(self):
        super(Packages, self).__init__()
        self.load_cache = False
        self.channels = {}

    def __cache_packages_for_channel(self, channel):
        print "Loading package cache for %s" % channel
        packages = self.channel_software_list_all_packages(channel)

        self.idIndex = {}
        self.nvreaIndex = {}

        for p in packages:
            self.__cache_package_for_channel(channel, p)

    def __cache_package_for_channel(self, channel, package):
        #print package
        nvra = "%s-%s-%s.%s" % (package['name'],
                                package['version'],
                                package['release'],
                                package['arch_label'])
        #print 'NVRA:', nvra
        self.channels[channel][nvra] = package['id']
        nvr = "%s-%s-%s" % (package['name'],
                            package['version'],
                            package['release'])
        #print 'NVR:', nvr
        self.channels[channel][nvr] = package['id']

    def get_channels(self):
        return self.channels.keys()

    def set_channels(self, channels, load_cache = False):
        self.load_cache = load_cache

        for channel in channels:
            self.channels[channel] = {}
            if self.load_cache:
                self.__cache_packages_for_channel(channel)

    def get_package_id(self, channel, name):
        if channel not in self.channels and self.load_cache:
            __cache_packages_for_channel(channel)

        if name in self.channels[channel]:
            return self.channels[channel][name]

        if self.load_cache:
            return None

        # For a reason I could not figure out, wildcard searches
        # would not work with this package filename:
        #
        #   perl-Sys-Guestfs-1.28.1-1.55.el7.centos.2.x86_64*
        #
        # But, it would work with others.  So, just search
        # both ways instead.
        escaped = self.__escape_re.sub(r'\\\1', name)
        query = 'filename:%s or filename:%s*' % (escaped, escaped)
        packages = self.packages_search_advanced(query)
        for pkg in packages:
            nvra = "%s-%s-%s.%s" % (pkg['name'],
                                    pkg['version'],
                                    pkg['release'],
                                    pkg['arch'])
            if nvra.startswith(name + "."):
                details = self.packages_get_details(pkg)
                if details is not None:
                    for chan in details['providing_channels']:
                        if channel == chan:
                            self.__cache_package_for_channel(channel, details)
                            return self.channels[channel][name]

        return None

