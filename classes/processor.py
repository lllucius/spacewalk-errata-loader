
from session import Session
from packages import Packages
from errata import Errata
from listarchive import ListArchive
from filearchive import FileArchive
from preprocessor import Preprocessors

class Processor(Session, Packages, Errata, ListArchive, FileArchive, Preprocessors):
    def __init__(self):
        super(Processor, self).__init__()
        self.__preprocs = None
        self.config = None

    def get_preprocs(self):
        if self.__preprocs is not None:
            return self.__preprocs.get()

        return []

    def process(self, config):
        self.config = config

        self.connect(self.config.server, self.config.user, self.config.password)

        self.init_errata_cache()

        self.set_channels(self.config.channels.split(','), self.config.load_cache)

        self.load_preprocessors(self.config.dist)

        if len(self.config.sources):
            for src in self.config.sources:
                self.process_file_messages(self.config, src)
        else:
            self.process_list_messages(self.config)

        self.disconnect()

