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

from .views import ProductParsingListView
# from .views import ProductParsingCreateView
from .views import product_parsing

from .parser_scheduler import start_product_parsing

urlpatterns = [
    path('', MarketplaceListView.as_view(), name='parser-marketplace-list'),
    path('marketplace/', MarketplaceListView.as_view(), name='parser-marketplace-list'),
    path('marketplace/<int:pk>/', MarketplaceDetailView.as_view(), name='parser-marketplace-detail'),
    path('marketplace/add', MarketplaceCreateView.as_view(), name='parser-marketplace-add'),
    path('marketplace/<int:pk>/update/', MarketplaceUpdateView.as_view(), name='parser-marketplace-update'),
    path('marketplace/<int:pk>/delete/', MarketplaceDeleteView.as_view(), name='parser-marketplace-delete'),

    path('category/', CategoryListView.as_view(), name='parser-category-list'),
    path('category/<int:pk>/', CategoryDetailView.as_view(), name='parser-category-detail'),
    path('category/add', CategoryCreateView.as_view(), name='parser-category-add'),
    path('category/<int:pk>/update/', CategoryUpdateView.as_view(), name='parser-category-update'),
    path('category/<int:pk>/delete/', CategoryDeleteView.as_view(), name='parser-category-delete'),

    path('product/', ProductListView.as_view(), name='parser-product-list'),
    path('product/<int:pk>/', ProductDetailView.as_view(), name='parser-product-detail'),
    path('product/<int:pk>/parse/', product_parsing, name='parser-product-parse'),

    path('product/add', ProductCreateView.as_view(), name='parser-product-add'),
    path('product/<int:pk>/update/', ProductUpdateView.as_view(), name='parser-product-update'),
    path('product/<int:pk>/delete/', ProductDeleteView.as_view(), name='parser-product-delete'),

    path('parsing-product/', ProductParsingListView.as_view(), name='parser-parsing-product-list'),
    # path('product/<int:pk>/', ProductDetailView.as_view(), name='parser-product-detail'),
    # path('parsing-product/add', ProductParsingCreateView.as_view(), name='parser-parsing-product-add'),
    # path('parsing-product/add', product_parsing, name='parser-parsing-product-add'),
    path('product/parse/', product_parsing, name='parser-product-parse'),
    # path('product/<int:pk>/delete/', ProductDeleteView.as_view(), name='parser-product-delete'),
]

# start scheduler
start_product_parsing()
