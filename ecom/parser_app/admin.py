from django.contrib import admin

from .models import Category
from .models import Marketplace
from .models import Product

admin.site.register(Category)
admin.site.register(Marketplace)
admin.site.register(Product)
