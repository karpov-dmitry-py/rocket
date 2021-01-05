from apscheduler.schedulers.background import BackgroundScheduler

from .helpers import _log
from .helpers import _err
from .models import ProductParsing


def process_product_parsing():
    # _log('This is a scheduled call of "process_product_parsing"')
    jobs = ProductParsing.objects.filter(status='created')
    for job in jobs:
        _log(f'Found job with status created: {job.id}')
    if not jobs:
        _log('No jobs to process found!')


def start_product_parsing():
    scheduler = BackgroundScheduler()
    scheduler.add_job(process_product_parsing, 'interval', seconds=10, max_instances=1)
    scheduler.start()
