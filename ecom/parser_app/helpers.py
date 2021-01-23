import logging
import sys
# noinspection PyPackageRequirements
import pytz
from datetime import datetime

logging.basicConfig(stream=sys.stdout, level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


def _log(msg):
    logging.info(msg)


def _err(msg):
    logging.error(msg)


def _now_as_str():
    _format = '%d-%m-%Y %H:%M:%S'
    return _now().strftime(_format)


def _now():
    return datetime.now(_timezone())


def _timezone():
    return pytz.timezone(zone='Europe/Moscow')


def _make_aware_time(_datetime):
    return _datetime.replace(tzinfo=_timezone())
