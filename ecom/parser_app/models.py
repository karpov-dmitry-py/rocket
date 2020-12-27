from django.db.models import Model
from django.db.models import CharField
from django.db.models import ForeignKey
from django.db.models import CASCADE


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
