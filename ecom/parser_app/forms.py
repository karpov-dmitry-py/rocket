from django.forms import ModelForm
from .views import ProductParsing
from .views import CategoryParsing

class ProductParsingCreateForm(ModelForm):

    class Meta:
        model = ProductParsing
        fields = ['product', 'region']


class CategoryParsingCreateForm(ModelForm):

    class Meta:
        model = CategoryParsing
        fields = ['category', 'region']
