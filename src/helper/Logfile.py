import logging
import os

class LogFile:
    def __init__(self, option):
        self.option = option
        ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
        os.makedirs(os.path.dirname(ROOT_DIR+'logs'), exist_ok=True)
        self.LOG_FILE_INFO = os.path.join(ROOT_DIR, '../../logs/info.log')
        self.LOG_FILE_ERROR = os.path.join(ROOT_DIR, '../../logs/error.log')
        self.log_setup = ''

    def setup_logger(self, logger_name, log_file, level=logging.INFO):
        log_setup = logging.getLogger(logger_name)
        formatter = logging.Formatter('%(asctime)s %(message)s')
        fileHandler = logging.FileHandler(log_file, mode='a')
        fileHandler.setFormatter(formatter)
        streamHandler = logging.StreamHandler()
        streamHandler.setFormatter(formatter)
        log_setup.setLevel(level)

        if (log_setup.hasHandlers()):
            log_setup.handlers.clear()
        log_setup.addHandler(fileHandler)
        log_setup.addHandler(streamHandler)
        self.log_setup = log_setup

    def logger(self, msg, level, logfile):
        if logfile == 'error':
            log = logging.getLogger('log_error')
        if logfile == 'info':
            log = logging.getLogger('log_info')

        if level == 'info':
            log.info(msg)
        if level == 'warning':
            log.warning(msg)
        if level == 'error':
            log.error(msg)

    def write(self, log_type, message):
        if not self.log_setup:
            self.setup_logger('log_error', self.LOG_FILE_ERROR)
            self.setup_logger('log_info', self.LOG_FILE_INFO)

        if log_type == 'error':
            if "daemon" == self.option:
                self.logger(message, 'error', 'error')
            else:
                print(message)
        else:
            if "daemon" == self.option:
                self.logger(message, 'info', 'info')
            else:
                print(message)
