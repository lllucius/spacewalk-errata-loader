
import re
import xmlrpclib

from log import *
from packages import *

class Session(object):

    def __init__(self):
        super(Session, self).__init__()
        self.servername = None
        self.user = None
        self.password = None
        self.url = None
        self.server = None
        self.key = None

    def connect(self, server, user, password):
        self.servername = server
        self.user = user
        self.password = password
        self.url = "https://" + self.servername + "/rpc/api"
        self.server = xmlrpclib.Server(self.url)
        self.auth_login(self.user, self.password)

    def disconnect(self):
        self.auth_logout()

    def auth_login(self, login, password):
        try:
            self.key = self.server.auth.login(login,
                                              password)
            return
        except xmlrpclib.Fault, f:
            if f.faultCode != -20:
                EXCEPTION("Failed to login")
                raise

        self.auth_login(login, password)

    def auth_logout(self):
        try:
            self.server.auth.logout(self.key)
            self.key = None
        except xmlrpclib.Fault, f:
            if f.faultCode != -20:
                EXCEPTION("Failed to logout")
                raise

    def channel_software_list_all_packages(self, channel):
        try:
            return self.server.channel.software.listAllPackages(self.key,
                                                                channel)
        except xmlrpclib.Fault, f:
            if f.faultCode != -20:
                raise

        self.auth_login(self.login, self.password)
        return self.channel_software_list_all_packages(channel)

    def packages_search_advanced(self, query):
        try:
            return self.server.packages.search.advanced(self.key,
                                                        query)
        except xmlrpclib.Fault, f:
            if f.faultCode != -20:
                raise

        self.auth_login(self.login, self.password)
        return self.packages_search_advanced(name, channel)

    def packages_get_details(self, package):
        try:
            return self.server.packages.getDetails(self.key,
                                                   package["id"])
        except xmlrpclib.Fault, f:
            if f.faultCode == -20:
                raise

        self.auth_login(self.login, self.password)
        return self.packages_get_details(name, channel)

    def errata_create(self, erratum):
        try:
            return self.server.errata.create(self.key,
                                             erratum.get_info_dict(),
                                             erratum.bugs,
                                             erratum.keywords,
                                             erratum.get_package_ids(),
                                             erratum.publish,
                                             erratum.channelLabel)
        except xmlrpclib.Fault, f:
            if f.faultCode == 2601:
                return None
            if f.faultCode != -20:
                raise

        self.auth_login(self.login, self.password)
        return self.errata_create(erratum)

    def errata_set_details(self, erratum, details):
        try:
            return self.server.errata.setDetails(self.key,
                                                 erratum.advisory_name,
                                                 details)

        except xmlrpclib.Fault, f:
            if f.faultCode != -20:
                raise

        self.auth_login(self.login, self.password)
        return self.errata_set_details(erratum, details)

    def errata_applicable_to_channels(self, erratum):
        try:
            return self.server.errata.applicable_to_channels(self.key,
                                                             erratum.advisory_name)
        except xmlrpclib.Fault, f:
            if f.faultCode != -20:
                raise

        self.auth_login(self.login, self.password)
        return self.errata_applicable_to_channels(erratum)

    def errata_publish(self, erratum):
        try:
            return self.server.errata.publish(self.key,
                                              erratum.advisory_name,
                                              erratum.channelLabel)
        except xmlrpclib.Fault, f:
            if f.faultCode != -20:
                raise

        self.auth_login(self.login, self.password)
        return self.errata_publish(erratum)

    def channel_list_software_channels(self):
        try:
            return self.server.channel.listSoftwareChannels(self.key)
        except xmlrpclib.Fault, f:
            if f.faultCode != -20:
                raise

        self.auth_login(self.login, self.password)
        return self.channel_list_software_channels()

    def software_list_errata(self, channel):
        try:
            return self.server.channel.software.listErrata(self.key, channel)
        except xmlrpclib.Fault, f:
            if f.faultCode != -20:
                raise

        self.auth_login(self.login, self.password)
        return self.software_list_errata(channel)

