from django.utils import timezone
from django.db.models import Model
from django.db.models import CharField
from django.db.models import TextField
from django.db.models import DateTimeField
from django.db.models import IntegerField
from django.db.models import ForeignKey
from django.db.models import CASCADE


class ModelHelper:
    PARSING_STATUSES = [
        ('created', 'created'),
        ('scheduled', 'scheduled'),
        ('progress', 'progress'),
        ('done', 'done'),
    ]

    @staticmethod
    def get_region_codes_by_ids(product_id, region_id):
        # noinspection PyUnresolvedReferences
        product = Product.objects.get(pk=product_id)
        # noinspection PyUnresolvedReferences
        region = Region.objects.get(pk=region_id)
        result = ModelHelper.get_region_codes_by_objects(product, region)
        return result

    @staticmethod
    def get_region_codes_by_ids_for_category(category_id, region_id):
        # noinspection PyUnresolvedReferences
        category = Category.objects.get(pk=category_id)
        # noinspection PyUnresolvedReferences
        region = Region.objects.get(pk=region_id)
        result = ModelHelper.get_region_codes_by_objects(category, region)
        return result

    @staticmethod
    def get_region_codes_by_objects(_object, region):
        marketplace = _object.marketplace
        # noinspection PyUnresolvedReferences
        rows = RegionCode.objects.filter(marketplace=marketplace).filter(region=region)
        if not rows:
            return
        return rows[0]

    @staticmethod
    def get_parsing_job_statuses():
        return ModelHelper.PARSING_STATUSES

    @staticmethod
    def get_parsing_job_initial_status():
        return ModelHelper.PARSING_STATUSES[0][1]


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
    status = CharField(max_length=100, null=False, choices=ModelHelper.get_parsing_job_statuses(),
                       default=ModelHelper.get_parsing_job_initial_status())
    result_file = CharField(max_length=1000, blank=True, null=True)
    comment = TextField(max_length=5000, blank=True, null=True)
    error = TextField(max_length=5000, blank=True, null=True)
    start_date = DateTimeField(default=timezone.now)
    end_date = DateTimeField(blank=True, null=True)
    duration = IntegerField(blank=True, null=True)

    def __str__(self):
        return f'{self.product}: {self.start_date}: {self.status}'


class CategoryParsing(Model):
    category = ForeignKey(Category, on_delete=CASCADE)
    region = ForeignKey(Region, on_delete=CASCADE)
    status = CharField(max_length=100, null=False, choices=ModelHelper.get_parsing_job_statuses(),
                       default=ModelHelper.get_parsing_job_initial_status())
    result_file = CharField(max_length=1000, blank=True, null=True)
    comment = TextField(max_length=5000, blank=True, null=True)
    error = TextField(max_length=5000, blank=True, null=True)
    start_date = DateTimeField(default=timezone.now)
    end_date = DateTimeField(blank=True, null=True)
    duration = IntegerField(blank=True, null=True)

    def __str__(self):
        return f'{self.category}: {self.start_date}: {self.status}'
