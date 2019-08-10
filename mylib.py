import logging


def xstr(s):
    """
    Convert s to a string

    :param s: the object to convert
    :return: a string representation of s (or *** if s is None)
    """
    return '***' if s is None else str(s)


def setup_logger(l):
    """
    Initialise the logger with a correct formatter

    :param l: the logger to configure
    """
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    l.addHandler(handler)
