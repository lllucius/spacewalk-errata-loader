#!/usr/bin/python -u
#
# Utility to load errata into Spacewalk
#
# Based on various other versions as described in the original
# comments below.
#
# My modifications are:
#
# Copyright (C) 2016 Leland Lucius (github@homerow.net)
#

#
# Original information included in code:
#
# Script which can process CentOS errata announcements and convert
# them to errata in spacewalk.  Based on rhn-tool.py by Lars Jonsson
#
# Latest version of the script may be obtained from
# http://www.bioss.ac.uk/staff/davidn/spacewalk-stuff/
#
# Copyright (C) 2012  Biomathematics and Statistics Scotland
#
# Author: Lars Jonsson (ljonsson@redhat.com)
#         David Nutter (davidn@bioss.ac.uk)
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
#

from argparse import *
from datetime import datetime
from ConfigParser import SafeConfigParser
import os
import sys

from classes.moduleloader import ModuleLoader
from version import *

#Config constants.
CONFIG_FILE="loader.cfg"

class StoreAction(Action):
    def __init__(self,
                 option_strings,
                 dest,
                 nargs=None,
                 const=None,
                 default=None,
                 type=None,
                 choices=None,
                 required=False,
                 help=None,
                 metavar=None):
        self._default = default
        self.type = type
        super(StoreAction, self).__init__(
                                          option_strings=option_strings,
                                          dest=dest,
                                          nargs=nargs,
                                          const=const,
                                          default=default,
                                          type=type,
                                          choices=choices,
                                          required=required,
                                          help=help,
                                          metavar=metavar,
                                         )

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)

    @property
    def default(self):
        dflt = self._default
        config = self.container.get_default('_config')
        section = self.container.get_default('_section')

        if config is None or self.dest is None:
            return dflt

        if section is None or not config.has_section(section):
            if config.has_section('DEFAULT'):
                section = 'DEFAULT'
            else:
                section = config.sections()[0]

        if not config.has_option(section, self.dest):
            return dflt

        if self.type == bool:
            dflt = config.getboolean(section, self.dest)
        elif self.type == float:
            dflt = config.getfloat(section, self.dest)
        elif self.type == int:
            dflt = config.getint(section, self.dest)
        else:
            dflt = config.get(section, self.dest)

        return dflt

    @default.setter
    def default(self, value):
        self._default = value

class StoreConstAction(StoreAction):
    def __init__(self,
                 option_strings,
                 dest,
                 const=None,
                 default=None,
                 type=None,
                 help=None):
        super(StoreConstAction, self).__init__(
                                               option_strings=option_strings,
                                               dest=dest,
                                               const=const,
                                               default=default,
                                               type=type,
                                               help=help,
                                               nargs=0,
                                               required=False,
                                              )

    def __call__(self, parser, namespace, values, option_string=None):
        super(StoreConstAction, self).__call__(
                                               parser,
                                               namespace,
                                               self.const,
                                               option_string=option_string
                                              )

class StoreTrueAction(StoreConstAction):
    def __init__(self,
                 option_strings,
                 dest,
                 default=None,
                 help=None):
        super(StoreTrueAction, self).__init__(
                                              option_strings=option_strings,
                                              dest=dest,
                                              default=default,
                                              help=help,
                                              type=bool,
                                              const=True,
                                             )

class StoreFalseAction(StoreConstAction):
    def __init__(self,
                 option_strings,
                 dest,
                 default=None,
                 help=None):
        super(StoreFalseAction, self).__init__(
                                               option_strings=option_strings,
                                               dest=dest,
                                               default=default,
                                               help=help,
                                               type=bool,
                                               const=False,
                                              )

def dateArg(str):
    try:
        ym = datetime.strptime(str, "%Y-%m").strftime("%Y-%m")
    except Exception, e:
        raise ArgumentTypeError(e)

    return ym

def process_args(loader):
    processor_names = loader.get_module_names()

    default_date = datetime(datetime.today().year, datetime.today().month, 1).strftime("%Y-%m")

    parser = ArgumentParser(version=VERSION)
    parser.register('action', None, StoreAction)
    parser.register('action', 'store', StoreAction)
    parser.register('action', 'store_const', StoreConstAction)
    parser.register('action', 'store_true', StoreTrueAction)
    parser.register('action', 'store_false', StoreFalseAction)

    parser.add_argument("dist", choices=processor_names,
                        help="The target distribution")
    parser.add_argument("sources", nargs="*",
                        help="List of files or URLs to pull errata from")

    group = parser.add_argument_group("server arguments")
    group.add_argument("-s", "--server", dest="server", type=str,
                      help="Spacewalk server hostname")
    group.add_argument("-u", "--user", dest="user", type=str,
                      help="Spacewalk userid")
    group.add_argument("-p", "--password", dest="password", type=str,
                      help="Spacewalk password (cleartext)")


    group = parser.add_argument_group("general arguments")
    group.add_argument("--use-list-digest", dest="use_list_digest", action="store_true",
                      help="Use the list digest instead of individual messages")
    group.add_argument("-l", "--load", dest="load_cache", action="store_true",
                      help="Load the package cache at startup")
    group.add_argument("-n", "--no-load", dest="load_cache", action="store_false",
                      help="Do not load the package cache at startup")
    group.add_argument("--dry-run", dest="dry_run", action="store_true",
                      help="Process the errata, but do not publish")

    group = parser.add_argument_group("errata arguments")
    group.add_argument("-c", "--channels", dest="channels", type=str,
                      help="List of channels where to publish errata, separated by comma")
    group.add_argument("-f", "--from", dest="from_date", type=dateArg, default=default_date,
                      help="Starting date (YYYY-MM) from which to pull errata.  Format 'listarchive' only")
    group.add_argument("-t", "--to", dest="to_date", type=dateArg, default=default_date,
                      help="Ending date (YYYY-MM) from which to pull errata.  Format 'listarchive' only")
    group.add_argument("--max-errata", dest="max_errata", type=int, default=10000,
                      help="Maximum number of errata to process at once.")
    group.add_argument("--publish-with-missing", dest="publish_with_missing", action="store_true",
                      help="Publish erratum even if packages are missing")
    group.add_argument("--report-missing", dest="report_missing", action="store_true",
                      help="Show packages that are missing")
    group.add_argument("--suppress-missing-group", dest="suppress_missing_group", action="store_true",
                      help="Do not show missing packages if all are missing for group")

    group = parser.add_argument_group("config arguments")
    group.add_argument("--conf", dest="config", type=str, default=CONFIG_FILE,
                      help="Read the specified config file instead of the default")
    group.add_argument("--show-config", dest="show_config", action="store_true",
                      help="Just print configuration information")

    for name in processor_names:
        module = loader.get_module(name)
        if hasattr(module, 'add_command_arguments'):
            group = parser.add_argument_group("%s arguments" % name)
            module.add_command_arguments(group)

    args = parser.parse_args()

    config = SafeConfigParser()
    with open(args.config) as f:
        config.readfp(f)

    parser.set_defaults(**{'_config': config, '_section': args.dist})

    args = parser.parse_args()

    delattr(args, '_config')
    delattr(args, '_section')

    return args

def main():
    loader = ModuleLoader()
    loader.load_modules('Processor', 'processors')

    config = process_args(loader)

    if config.show_config:
        print "Current configuration:"
        for var in sorted(vars(config)):
            print "%-32s = %s" % (var, getattr(config, var))
        sys.exit(0)

    loader.get_module(config.dist).process(config)

if __name__ == "__main__":
    main()

