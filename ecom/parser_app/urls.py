from django.urls import path

from .views import MarketplaceListView
from .views import MarketplaceDetailView
from .views import MarketplaceCreateView
from .views import MarketplaceUpdateView
from .views import MarketplaceDeleteView

from .views import CategoryListView
from .views import CategoryDetailView
from .views import CategoryCreateView
from .views import CategoryUpdateView
from .views import CategoryDeleteView

from .views import ProductListView
from .views import ProductDetailView
from .views import ProductCreateView
from .views import ProductUpdateView
from .views import ProductDeleteView

from .views import RegionListView
from .views import RegionDetailView
from .views import RegionCreateView
from .views import RegionUpdateView
from .views import RegionDeleteView

from .views import RegionCodeListView
from .views import RegionCodeDetailView
from .views import RegionCodeCreateView
from .views import RegionCodeUpdateView
from .views import RegionCodeDeleteView

from .views import ProductParsingListView
from .views import ProductParsingDetailView
from .views import ProductParsingUpdateView
from .views import ProductParsingDeleteView

from .views import product_parsing

urlpatterns = [

    # marketplace
    path('', MarketplaceListView.as_view(), name='parser-marketplace-list'),
    path('marketplace/', MarketplaceListView.as_view(), name='parser-marketplace-list'),
    path('marketplace/<int:pk>/', MarketplaceDetailView.as_view(), name='parser-marketplace-detail'),
    path('marketplace/add', MarketplaceCreateView.as_view(), name='parser-marketplace-add'),
    path('marketplace/<int:pk>/update/', MarketplaceUpdateView.as_view(), name='parser-marketplace-update'),
    path('marketplace/<int:pk>/delete/', MarketplaceDeleteView.as_view(), name='parser-marketplace-delete'),

    # category
    path('category/', CategoryListView.as_view(), name='parser-category-list'),
    path('category/<int:pk>/', CategoryDetailView.as_view(), name='parser-category-detail'),
    path('category/add', CategoryCreateView.as_view(), name='parser-category-add'),
    path('category/<int:pk>/update/', CategoryUpdateView.as_view(), name='parser-category-update'),
    path('category/<int:pk>/delete/', CategoryDeleteView.as_view(), name='parser-category-delete'),

    # product
    path('product/', ProductListView.as_view(), name='parser-product-list'),
    path('product/<int:pk>/', ProductDetailView.as_view(), name='parser-product-detail'),
    path('product/<int:pk>/parse/', product_parsing, name='parser-product-parse'),
    path('product/add', ProductCreateView.as_view(), name='parser-product-add'),
    path('product/<int:pk>/update/', ProductUpdateView.as_view(), name='parser-product-update'),
    path('product/<int:pk>/delete/', ProductDeleteView.as_view(), name='parser-product-delete'),

    # region
    path('region/', RegionListView.as_view(), name='parser-region-list'),
    path('region/<int:pk>/', RegionDetailView.as_view(), name='parser-region-detail'),
    path('region/add', RegionCreateView.as_view(), name='parser-region-add'),
    path('region/<int:pk>/update/', RegionUpdateView.as_view(), name='parser-region-update'),
    path('region/<int:pk>/delete/', RegionDeleteView.as_view(), name='parser-region-delete'),

    # region code
    path('region_code/', RegionCodeListView.as_view(), name='parser-region-code-list'),
    path('region_code/<int:pk>/', RegionCodeDetailView.as_view(), name='parser-region-code-detail'),
    path('region_code/add', RegionCodeCreateView.as_view(), name='parser-region-code-add'),
    path('region_code/<int:pk>/update/', RegionCodeUpdateView.as_view(), name='parser-region-code-update'),
    path('region_code/<int:pk>/delete/', RegionCodeDeleteView.as_view(), name='parser-region-code-delete'),

    # parsing product
    path('parsing-product/', ProductParsingListView.as_view(), name='parser-parsing-product-list'),
    path('parsing-product/<int:pk>/', ProductParsingDetailView.as_view(), name='parser-parsing-product-detail'),
    path('product/parse/', product_parsing, name='parser-product-parse'), # add new parsing job
    path('parsing-product/<int:pk>/update/', ProductParsingUpdateView.as_view(), name='parser-parsing-product-update'),
    path('parsing-product/<int:pk>/delete/', ProductParsingDeleteView.as_view(), name='parser-parsing-product-delete'),
]
