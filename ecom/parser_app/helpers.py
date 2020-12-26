import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def _log(msg):
    logging.info(msg)


def _err(msg):
    logging.error(msg)
