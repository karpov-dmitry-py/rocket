from django.db.models import Model
from django.db.models import CharField
from django.db.models import ForeignKey
from django.db.models import CASCADE


class Category(Model):
    name = CharField(max_length=200, null=False)

    def __str__(self):
        return f'{self.name}'


class Marketplace(Model):
    name = CharField(max_length=100, null=False)
    url = CharField(max_length=200, null=False)

    def __str__(self):
        return f'{self.name}'


class CategoryUrl(Model):
    category = ForeignKey(Category, on_delete=CASCADE)
    marketplace = ForeignKey(Marketplace, on_delete=CASCADE)
    url = CharField(max_length=1000, null=False)

    def __str__(self):
        return f'URL for: {self.marketplace} -> {self.category}'


class ProductUrl(Model):
    name = CharField(max_length=200, null=False)
    marketplace = ForeignKey(Marketplace, on_delete=CASCADE)
    url = CharField(max_length=1000, null=False)

    def __str__(self):
        return f'URL for: {self.marketplace} -> {self.name}'
