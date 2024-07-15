import logging  # pragma: no cover

FORMAT = "%(levelname)s: %(message)s"  # pragma: no cover
logging.basicConfig(format=FORMAT)  # pragma: no cover


def set_loglevel(level):  # pragma: no cover
    logging.basicConfig(
        format=FORMAT,
        level=getattr(logging, level),
    )
