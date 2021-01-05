from django.forms import ModelForm
from .views import ProductParsing

class ProductParsingCreateForm(ModelForm):

    class Meta:
        model = ProductParsing
        fields = ['product', 'region']
