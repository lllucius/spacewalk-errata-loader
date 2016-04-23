
from errata import Errata
from filearchive import FileArchive
from listarchive import ListArchive
from log import *
from moduleloader import Module
from packages import Packages
from preprocessor import Preprocessors
from session import Session


class ProcessorBase(Module, Session, Packages, Errata, ListArchive, FileArchive, Preprocessors):
    def __init__(self, module_name):
        super(ProcessorBase, self).__init__(module_name)
        self.errata_processed = 0
        self.config = None

    def process(self, config):
        self.config = config

        self.connect(self.config.server, self.config.user, self.config.password)

        self.init_errata_cache()

        self.set_channels(self.config.channels.split(","), self.config.load_cache)

        self.load_preprocessors(self.config.dist)

        if len(self.config.sources):
            for src in self.config.sources:
                self.process_file_messages(self.config, src)
        else:
            self.process_list_messages(self.config)

        self.disconnect()

