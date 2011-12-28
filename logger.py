#!/usr/local/bin/python

import logging
import sys

#The background is set with 40 plus the number of the color, and the foreground with 30

#These are the sequences need to get colored ouput
RESET_SEQ = "\033[0m"
COLOR_SEQ = "\033[1;%dm"
BOLD_SEQ = "\033[1m"

def formatter_message(message, use_color = True):
    if use_color:
        message = message.replace("$RESET", RESET_SEQ).replace("$BOLD", BOLD_SEQ)
    else:
        message = message.replace("$RESET", "").replace("$BOLD", "")
    return message

COLORS = {
    'WARNING': 1,
    'INFO': 2,
    'DEBUG': 3,
    'CRITICAL': 4,
    'ERROR': 5
}

class ColoredFormatter(logging.Formatter):
    def __init__(self, msg, use_color = True):
        logging.Formatter.__init__(self, msg, datefmt="%H:%M:%S")
        self.use_color = use_color

    def format(self, record):
        levelname = record.levelname
        if self.use_color and levelname in COLORS:
            levelname_color = COLOR_SEQ % (31 + COLORS[levelname]) + levelname + RESET_SEQ
            record.levelname = levelname_color
        return logging.Formatter.format(self, record)


# Custom logger class with multiple destinations
class ColoredLogger(logging.Logger):
    #FORMAT = "[$BOLD%(name)-s$RESET][%(levelname)-s]  %(message)s ($BOLD%(filename)s$RESET:%(lineno)d)"
    FORMAT = "%(asctime)s [$BOLD%(name)-s$RESET][%(levelname)-s]  %(message)s"
    COLOR_FORMAT = formatter_message(FORMAT, True)

    def __init__(self, name):

        logging.Logger.__init__(self, name)

        color_formatter = ColoredFormatter(self.COLOR_FORMAT)

        console = logging.StreamHandler()
        console.setFormatter(color_formatter)

        self.addHandler(console)
        return


