from django.views.generic import ListView
from django.views.generic import DetailView
from django.views.generic import CreateView
from django.views.generic import UpdateView
from django.views.generic import DeleteView

from .models import Marketplace
from .models import Category
from .models import Product
from .models import ProductParsing


# marketplace
class MarketplaceListView(ListView):
    model = Marketplace
    template_name = 'parser_app/marketplace_list.html'
    context_object_name = 'marketplaces'
    ordering = ['id']


class MarketplaceDetailView(DetailView):
    model = Marketplace
    fields = ['name', 'url']


class MarketplaceCreateView(CreateView):
    model = Marketplace
    fields = ['name', 'url']
    success_url = '/'


class MarketplaceUpdateView(UpdateView):
    model = Marketplace
    fields = ['name', 'url']
    success_url = '/'


class MarketplaceDeleteView(DeleteView):
    model = Marketplace
    success_url = '/'


# category
class CategoryListView(ListView):
    model = Category
    template_name = 'parser_app/category_list.html'
    context_object_name = 'categories'
    ordering = ['id']


class CategoryDetailView(DetailView):
    model = Category
    fields = ['name', 'url', 'marketplace']


class CategoryCreateView(CreateView):
    model = Category
    fields = ['name', 'url', 'marketplace']
    success_url = '/category'


class CategoryUpdateView(UpdateView):
    model = Category
    fields = ['name', 'url', 'marketplace']
    success_url = '/category'


class CategoryDeleteView(DeleteView):
    model = Category
    success_url = '/category'


# product
class ProductListView(ListView):
    model = Product
    template_name = 'parser_app/product_list.html'
    context_object_name = 'products'
    ordering = ['id']


class ProductDetailView(DetailView):
    model = Product
    fields = ['name', 'url', 'marketplace']


class ProductCreateView(CreateView):
    model = Product
    fields = ['name', 'url', 'marketplace']
    success_url = '/product'


class ProductUpdateView(UpdateView):
    model = Product
    fields = ['name', 'url', 'marketplace']
    success_url = '/product'


class ProductDeleteView(DeleteView):
    model = Product
    success_url = '/product'


# product parsing
class ProductParsingListView(ListView):
    model = ProductParsing
    template_name = 'parser_app/productparsing_list.html'
    context_object_name = 'items'
    ordering = ['id']


class ProductParsingCreateView(CreateView):
    model = ProductParsing
    fields = ['product', 'region']
    success_url = '/parsing-product'
