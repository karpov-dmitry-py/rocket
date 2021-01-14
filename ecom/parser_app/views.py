from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist

from django.views.generic import ListView
from django.views.generic import DetailView
from django.views.generic import CreateView
from django.views.generic import UpdateView
from django.views.generic import DeleteView

from .models import Marketplace
from .models import Category
from .models import Product
from .models import Region
from .models import RegionCode
from .models import ProductParsing
from .models import CategoryParsing

from .forms import ProductParsingCreateForm
from .forms import CategoryParsingCreateForm
from .models import ModelHelper
from .parser_scheduler import start_parsing


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


# region
class RegionListView(ListView):
    model = Region
    template_name = 'parser_app/region_list.html'
    context_object_name = 'regions'
    ordering = ['id']


class RegionDetailView(DetailView):
    model = Region
    fields = ['name', ]


class RegionCreateView(CreateView):
    model = Region
    fields = ['name', ]
    success_url = '/region'


class RegionUpdateView(UpdateView):
    model = Region
    fields = ['name']
    success_url = '/region'


class RegionDeleteView(DeleteView):
    model = Region
    success_url = '/region'


# region code
class RegionCodeListView(ListView):
    model = RegionCode
    template_name = 'parser_app/regioncode_list.html'
    context_object_name = 'region_codes'
    ordering = ['id']


class RegionCodeDetailView(DetailView):
    model = RegionCode
    fields = ['region', 'marketplace', 'code']


class RegionCodeCreateView(CreateView):
    model = RegionCode
    fields = ['region', 'marketplace', 'code']
    success_url = '/region_code'


class RegionCodeUpdateView(UpdateView):
    model = RegionCode
    fields = ['region', 'marketplace', 'code']
    success_url = '/region_code'


class RegionCodeDeleteView(DeleteView):
    model = RegionCode
    success_url = '/region_code'


# product parsing
class ProductParsingListView(ListView):
    model = ProductParsing
    template_name = 'parser_app/productparsing_list.html'
    context_object_name = 'items'
    ordering = ['id']


class ProductParsingDetailView(DetailView):
    model = ProductParsing
    context_object_name = 'item'
    fields = ['product', 'region', 'start_date', 'end_date', 'status', 'result_file', 'comment', 'error',
              'duration', ]


class ProductParsingUpdateView(UpdateView):
    model = ProductParsing
    fields = ['product', 'region', 'start_date', 'end_date', 'status', 'result_file', 'comment', 'error',
              'duration', ]
    success_url = '/parsing-product'


class ProductParsingDeleteView(DeleteView):
    model = ProductParsing
    success_url = '/parsing-product'


def product_parsing(request, pk=None):
    if request.method == 'POST':
        product_id = request.POST.get('product')
        region_id = request.POST.get('region')
        db_row = ModelHelper.get_region_codes_by_ids(product_id, region_id)
        if not db_row:
            messages.error(request, f"Please add region code for selected product's marketplace to db and try again!")
            # redirecting user to where he came from
            redirect_view_name = request.resolver_match.view_name
            return redirect(redirect_view_name)
        form = ProductParsingCreateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f'A new product parsing job has been created!')
            return redirect('parser-parsing-product-list')
    else:
        if pk is not None:
            try:
                # noinspection PyUnresolvedReferences
                product = Product.objects.get(pk=pk)
            except ObjectDoesNotExist:
                messages.error(request, f'Product with id: {pk} does not exist in db!')
                return redirect('parser-product-list')
            initial = {'product': product}
            form = ProductParsingCreateForm(initial=initial)
        else:
            form = ProductParsingCreateForm()

    context = {'form': form}
    return render(request, 'parser_app/productparsing_form.html', context)


# category parsing
class CategoryParsingListView(ListView):
    template_name = 'parser_app/categoryparsing_list.html'
    model = CategoryParsing
    context_object_name = 'items'
    ordering = ['id']


class CategoryParsingDetailView(DetailView):
    model = CategoryParsing
    context_object_name = 'item'
    fields = ['category', 'region', 'start_date', 'end_date', 'status', 'result_file', 'comment', 'error',
              'duration', ]


class CategoryParsingUpdateView(UpdateView):
    model = CategoryParsing
    fields = ['category', 'region', 'start_date', 'end_date', 'status', 'result_file', 'comment', 'error',
              'duration', ]
    success_url = '/parsing-category'


class CategoryParsingDeleteView(DeleteView):
    model = CategoryParsing
    success_url = '/parsing-category'


def category_parsing(request, pk=None):
    if request.method == 'POST':
        category_id = request.POST.get('category')
        region_id = request.POST.get('region')
        db_row = ModelHelper.get_region_codes_by_ids_for_category(category_id, region_id)
        if not db_row:
            messages.error(request, f"Please add region code for selected category's marketplace to db and try again!")
            # redirecting user to where he came from
            redirect_view_name = request.resolver_match.view_name
            return redirect(redirect_view_name)
        form = CategoryParsingCreateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f'A new category parsing job has been created!')
            return redirect('parser-parsing-category-list')
    else:
        if pk is not None:
            try:
                # noinspection PyUnresolvedReferences
                category = Category.objects.get(pk=pk)
            except ObjectDoesNotExist:
                messages.error(request, f'Category with id: {pk} does not exist in db!')
                return redirect('parser-product-list')
            initial = {'category': category}
            form = CategoryParsingCreateForm(initial=initial)
        else:
            form = CategoryParsingCreateForm()

    context = {'form': form}
    return render(request, 'parser_app/categoryparsing_form.html', context)

# start scheduler to monitor db for new parsing jobs
start_parsing()
