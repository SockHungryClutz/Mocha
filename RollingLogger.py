# Class for logging stuff.
# Made by SockHungryClutz
#
# To use:
#   logger = RollingLogger_Sync(LogFileName(str), MaxLogFileSize(int),
#                               MaxNumberOfLogFiles(int), LoggingLevel(int))
# From there, call logger.[debug/info/warning/error/critical](Message) to log
# Use logger.closeLog() when closing to clean up everything else
# Log Levels:
#   5 = debug
#   4 = info
#   3 = warning
#   2 = error
#   1 = critical
#
# Setting a level means no messages less important than the level you choose will be logged.
# Setting level to 0 means nothing will be logged and the logger is just a dummy.

import logging
from logging.handlers import RotatingFileHandler
import time
from datetime import datetime

class RollingLogger_Sync:
    def __init__(self, name, fileSize, numFile, level):
        if level == 0:
            self.nologs = True
        else:
            self.logger = logging.getLogger(name)
            if level == 1:
                self.logger.setLevel(logging.CRITICAL)
            elif level == 2:
                self.logger.setLevel(logging.ERROR)
            elif level == 3:
                self.logger.setLevel(logging.WARNING)
            elif level == 4:
                self.logger.setLevel(logging.INFO)
            else:
                self.logger.setLevel(logging.DEBUG)
            self.nologs = False
            self.handler = RotatingFileHandler(name+".log", maxBytes=fileSize, backupCount=numFile)
            self.logger.addHandler(self.handler)
            self.logger.info(">Logger " + name + " initialized - " + str(datetime.now()) + "<")

    def debug(self, msg):
        if not self.nologs:
            self.logger.debug("[" + str(datetime.now()) + "] *   " +msg)

    def info(self, msg):
        if not self.nologs:
            self.logger.info("[" + str(datetime.now()) + "]     " +msg)

    def warning(self, msg):
        if not self.nologs:
            self.logger.warning("[" + str(datetime.now()) + "] !   " +msg)

    def error(self, msg):
        if not self.nologs:
            self.logger.error("[" + str(datetime.now()) + "] !!  " +msg)

    def critical(self, msg):
        if not self.nologs:
            self.logger.critical("[" + str(datetime.now()) + "] !!! " +msg)
