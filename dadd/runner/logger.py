import logging


def get_logger(filename=None):
    logger = logging.getLogger('dadd_runner')
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        fmt='%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s'
    )

    console = logging.StreamHandler()
    console.setFormatter(formatter)

    filehandler = logging.FileHandler(filename or 'output.log')
    filehandler.setFormatter(formatter)

    logger.addHandler(console)
    logger.addHandler(filehandler)

    return logger
