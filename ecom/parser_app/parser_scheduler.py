import atexit
import time

from apscheduler.schedulers.background import BackgroundScheduler

from .helpers import _log
from .models import ProductParsing
from .models import ModelHelper

# from .parser import Parser
from .parser import Parser


def process_product_parsing():
    initial_status = 'created'
    next_status = 'scheduled'
    # noinspection PyUnresolvedReferences
    jobs = ProductParsing.objects.filter(status=initial_status)
    if not jobs:
        _log('Found no product parsing jobs to be processed.')
        return
    for job in jobs:
        job.status = next_status
        job.save()
        _log(f'Found a product parsing job to be processed with id: {job.id}')
    for job in jobs:
        product = job.product
        region = job.region
        url = product.url
        db_row = ModelHelper.get_region_codes_by_objects(product, region)
        # actual parsing start
        Parser(
            url=url,
            region=str(region),
            region_code=db_row.code,
            _type='product'
        )


def start_product_parsing():
    scheduler = BackgroundScheduler()
    scheduler.add_job(process_product_parsing, 'interval', seconds=10, max_instances=10)
    scheduler.start()
    atexit.register(lambda: scheduler.shutdown())
    # while True:
    #     time.sleep(10)
