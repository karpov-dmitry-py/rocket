from django.contrib import admin

from .models import Category
from .models import Marketplace
from .models import CategoryUrl
from .models import ProductUrl

admin.site.register(Category)
admin.site.register(Marketplace)
admin.site.register(CategoryUrl)
admin.site.register(ProductUrl)
