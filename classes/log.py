
import logging
import logging.config

class Log(object):
    def __init__(self):
        super(Log, self).__init__()
        logging.basicConfig(level=logging.CRITICAL)
        self.logger = logging.getLogger("preconfig")
 
    def set_config(self, config_file, verbose=None, debug=None):

        logging.config.fileConfig(config_file)
        self.logger = logging.getLogger("root")

        if debug is not None and debug:
            level = logging.DEBUG
        elif verbose is not None and verbose:
            level = logging.INFO
        else:
            level = None

        if level is not None:
            self.logger.setLevel(level)
            for handler in logging.root.handlers:
                handler.setLevel(level)

    def debug(self,*args, **kwargs):
        self.logger.debug(*args, **kwargs)

    def info(self,*args, **kwargs):
        self.logger.info(*args, **kwargs)

    def warn(self, *args, **kwargs):
        self.logger.warn(*args, **kwargs)

    def error(self, *args, **kwargs):
        self.logger.error(*args, **kwargs)

    def critical(self, *args, **kwargs):
        self.logger.critical(*args, **kwargs)

    def exception(self, *args, **kwargs):
        self.logger.exception(*args, **kwargs)

def DEBUG(*args, **kwargs):
    get_logger().debug(*args, **kwargs)

def INFO(*args, **kwargs):
    get_logger().info(*args, **kwargs)

def WARN(*args, **kwargs):
    get_logger().warn(*args, **kwargs)

def ERROR(*args, **kwargs):
    get_logger().error(*args, **kwargs)

def CRITICAL(*args, **kwargs):
    get_logger().critical(*args, **kwargs)

def EXCEPTION(*args, **kwargs):
    get_logger().exception(*args, **kwargs)

def get_logger():
    global __logger

    if '__logger' not in globals():
        __logger = Log()

    return __logger

