import atexit

from apscheduler.schedulers.background import BackgroundScheduler

from .helpers import _log, _err
from .models import ProductParsing
from .models import CategoryParsing
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


    # noinspection PyUnresolvedReferences
    jobs = ProductParsing.objects.filter(status=initial_status)
    for job in jobs:
        job.status = next_status
        job.save()
        _log(f'Found a product parsing job to be processed with id: {job.id}')
    for job in jobs:
        product = job.product
        region = job.region
        db_row = ModelHelper.get_region_codes_by_objects(product, region)

        # actual parsing start
        Parser(
            job=job,
            region_code=db_row.code if db_row else None,
            _type='product'
        )


def process_category_parsing():
    initial_status = 'created'
    next_status = 'scheduled'
    # noinspection PyUnresolvedReferences
    jobs = CategoryParsing.objects.filter(status=initial_status)
    if not jobs:
        _log('Found no category parsing jobs to be processed.')
        process_product_parsing()


    # noinspection PyUnresolvedReferences
    jobs = CategoryParsing.objects.filter(status=initial_status)
    for job in jobs:
        job.status = next_status
        job.save()
        _log(f'Found a category parsing job to be processed with id: {job.id}')
    for job in jobs:
        category = job.category
        region = job.region
        db_row = ModelHelper.get_region_codes_by_objects(category, region)

        # actual parsing start
        Parser(
            job=job,
            region_code=db_row.code if db_row else None,
            _type='category'
        )


def start_parsing():
    scheduler = BackgroundScheduler()
    # scheduler.add_job(process_product_parsing, 'interval', seconds=20, max_instances=10)
    scheduler.add_job(process_category_parsing, 'interval', seconds=10, max_instances=100)
    scheduler.start()
    atexit.register(lambda: scheduler.shutdown())
