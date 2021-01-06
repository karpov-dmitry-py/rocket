from django.utils import timezone
from django.db.models import Model
from django.db.models import CharField
from django.db.models import TextField
from django.db.models import DateTimeField
from django.db.models import IntegerField
from django.db.models import ForeignKey
from django.db.models import CASCADE

PARSING_STATUSES = [
    ('created', 'created'),
    ('scheduled', 'scheduled'),
    ('progress', 'progress'),
    ('done', 'done'),
]


class Marketplace(Model):
    name = CharField(max_length=100, null=False)
    url = CharField(max_length=200, null=False)

    def __str__(self):
        return f'{self.name}'


class Category(Model):
    name = CharField(max_length=500, null=False)
    url = CharField(max_length=1000, null=False)
    marketplace = ForeignKey(Marketplace, on_delete=CASCADE)

    def __str__(self):
        return f'{self.marketplace} -> {self.name}'


class Product(Model):
    name = CharField(max_length=500, null=False)
    url = CharField(max_length=1000, null=False)
    marketplace = ForeignKey(Marketplace, on_delete=CASCADE)

    def __str__(self):
        return f'{self.marketplace} -> {self.name}'


class Region(Model):
    name = CharField(max_length=500, null=False)

    def __str__(self):
        return self.name


class RegionCode(Model):
    region = ForeignKey(Region, on_delete=CASCADE)
    marketplace = ForeignKey(Marketplace, on_delete=CASCADE)
    code = CharField(max_length=50, null=False)

    def __str__(self):
        return f'{self.region}: {self.marketplace}: {self.code}'


class ProductParsing(Model):
    product = ForeignKey(Product, on_delete=CASCADE)
    region = ForeignKey(Region, on_delete=CASCADE)
    status = CharField(max_length=100, null=False, choices=PARSING_STATUSES, default='created')
    result_file = CharField(max_length=1000, blank=True, null=True)
    comment = TextField(max_length=5000, blank=True, null=True)
    error = TextField(max_length=5000, blank=True, null=True)
    start_date = DateTimeField(default=timezone.now)
    end_date = DateTimeField(blank=True, null=True)
    duration = IntegerField(blank=True, null=True)

    def __str__(self):
        return f'{self.product}: {self.start_date}: {self.status}'


class Helper:

    @staticmethod
    def get_region_codes_by_ids(product_id, region_id):
        # noinspection PyUnresolvedReferences
        product = Product.objects.get(pk=product_id)
        # noinspection PyUnresolvedReferences
        region = Region.objects.get(pk=region_id)
        result = Helper.get_region_codes_by_objects(product, region)
        return result

    @staticmethod
    def get_region_codes_by_objects(product, region):
        marketplace = product.marketplace
        # noinspection PyUnresolvedReferences
        result = RegionCode.objects.filter(marketplace=marketplace).filter(region=region)
        return result
