from django.contrib import admin

from .models import Category
from .models import Marketplace
from .models import Product
from .models import Region
from .models import RegionCode
from .models import ProductParsing

admin.site.register(Category)
admin.site.register(Marketplace)
admin.site.register(Product)
admin.site.register(Region)
admin.site.register(RegionCode)
admin.site.register(ProductParsing)
