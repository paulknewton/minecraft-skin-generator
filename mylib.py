import logging


def xstr(s):
    return '***' if s is None else str(s)


def todo(logger, s):
    logger.info("*** TODO: " + s)


def setup_logger(l):
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    l.addHandler(handler)
