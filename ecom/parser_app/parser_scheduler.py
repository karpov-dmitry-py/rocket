from apscheduler.schedulers.background import BackgroundScheduler

from .helpers import _log
from .helpers import _err
from .models import ProductParsing


def process_product_parsing():
    jobs = ProductParsing.objects.filter(status='created')
    new_status = 'scheduled'
    for job in jobs:
        job.status = new_status
        job.save()
        _log(f'Found a product parsing job to be processed with id: {job.id}')
    if not jobs:
        _log('No product parsing jobs to be processed found.')


def start_product_parsing():
    scheduler = BackgroundScheduler()
    scheduler.add_job(process_product_parsing, 'interval', seconds=10, max_instances=1)
    scheduler.start()
